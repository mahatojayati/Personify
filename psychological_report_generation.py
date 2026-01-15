import streamlit as st
import pylast
from openai import OpenAI

# Load credentials safely from Streamlit Secrets
LASTAPI_KEY = st.secrets.get("LASTFM_API_KEY")
LASTFM_SECRET = st.secrets.get("LASTFM_API_SECRET")
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN")

def get_musical_summary(username):
    """Fetches music data from Last.fm and generates an OCEAN profile via GitHub Models."""
    
    # 1. Validation check for API keys
    if not all([LASTAPI_KEY, LASTFM_SECRET, GITHUB_TOKEN]):
        return "⚠️ Configuration Error: API keys missing. Check .streamlit/secrets.toml"

    try:
        # 2. Connect to Last.fm
        network = pylast.LastFMNetwork(api_key=LASTAPI_KEY, api_secret=LASTFM_SECRET)
        user = network.get_user(username)
        top_tracks = user.get_top_tracks(limit=15)
        
        if not top_tracks:
            return f"No listening history found for user '{username}'. Ensure the profile is public."

        # 3. Aggregate genre tags
        tag_counts = {}
        for item in top_tracks:
            tags = item.item.get_top_tags(limit=5)
            for tag in tags:
                name = tag.item.get_name().lower()
                tag_counts[name] = tag_counts.get(name, 0) + 1
        
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)      
        tag_string = ", ".join([f"{tag} ({count})" for tag, count in sorted_tags[:15]])
        
        # 4. Initialize GitHub Models Client (Azure Inference Endpoint)
        client = OpenAI(
            base_url="https://models.inference.ai.azure.com",
            api_key=GITHUB_TOKEN,
        )
        
        # 5. Generate the AI Report using a high-performance model
        response = client.chat.completions.create(
            model="gpt-4o-mini", # Highly efficient for text analysis
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "You are a professional Music Psychologist. "
                        "Analyze the user's music tags using the Big Five (OCEAN) framework. "
                        "Provide a supportive, structured report with: "
                        "1. Personality Summary, 2. OCEAN Score Breakdown (Openness, Conscientiousness, "
                        "Extraversion, Agreeableness, Neuroticism), and 3. Emotional Regulation Style."
                    )
                },
                {"role": "user", "content": f"Music patterns to analyze: {tag_string}"}
            ],
            temperature=0.7,
        )
        
        return response.choices[0].message.content

    except pylast.PyLastError as e:
        return f"Last.fm Error: {e}. Is the username correct?"
    except Exception as e:
        return f"Technical Error: {str(e)}"
