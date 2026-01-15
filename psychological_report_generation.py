import streamlit as st
import pylast
from openai import OpenAI

# Load credentials from secrets
LASTAPI_KEY = st.secrets.get("LASTFM_API_KEY")
LASTFM_SECRET = st.secrets.get("LASTFM_API_SECRET")
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN")

def get_musical_summary(username):
    """Fetches user tags and generates a report using GitHub Models."""
    if not all([LASTAPI_KEY, LASTFM_SECRET, GITHUB_TOKEN]):
        return "⚠️ Configuration Error: API keys not found in Streamlit Secrets."

    try:
        # 1. Initialize Last.fm
        network = pylast.LastFMNetwork(api_key=LASTAPI_KEY, api_secret=LASTFM_SECRET)
        user = network.get_user(username)
        top_tracks = user.get_top_tracks(limit=15)
        
        if not top_tracks:
            return "No listening history found. Ensure the Last.fm profile is public."

        # 2. Extract and count tags
        tag_counts = {}
        for item in top_tracks:
            tags = item.item.get_top_tags(limit=5)
            for tag in tags:
                name = tag.item.get_name().lower()
                tag_counts[name] = tag_counts.get(name, 0) + 1
        
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)      
        tag_string = ", ".join([f"{tag} ({count})" for tag, count in sorted_tags[:15]])
        
        # 3. Initialize GitHub Models Client
        # GitHub Models uses the Azure Inference endpoint
        client = OpenAI(
            base_url="https://models.inference.ai.azure.com",
            api_key=GITHUB_TOKEN,
        )
        
        # 4. Generate Analysis using Llama 3.3 (or any available GitHub model)
        response = client.chat.completions.create(
            model="meta-llama-3.1-405b", # You can also use 'gpt-4o' if available to you
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a Music Psychologist. Analyze music tags using the Big Five (OCEAN) framework. "
                        "Provide a professional, insight-heavy report with: "
                        "1. Summary, 2. The Five Pillars (OCEAN breakdown), and 3. Emotional Regulation Style."
                    )
                },
                {
                    "role": "user",
                    "content": f"Analyze these music patterns: {tag_string}"
                }
            ],
            temperature=0.7,
            max_tokens=1000,
        )
        
        return response.choices[0].message.content

    except Exception as e:
        return f"❌ Error: {str(e)}"
