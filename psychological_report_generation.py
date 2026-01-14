import streamlit as st
import pylast
from groq import Groq

# Accessing keys via Streamlit's secrets
LASTAPI_KEY = st.secrets.get("LASTFM_API_KEY")
LASTFM_SECRET = st.secrets.get("LASTFM_API_SECRET")
GROQ_KEY = st.secrets.get("GROQ_API_KEY")

def get_musical_summary(username):
    """Fetches user tags and generates a report using Groq (Llama 3)."""
    if not all([LASTAPI_KEY, LASTFM_SECRET, GROQ_KEY]):
        return "⚠️ Configuration Error: API keys not found in Streamlit Secrets."

    try:
        # 1. Initialize Last.fm
        network = pylast.LastFMNetwork(api_key=LASTAPI_KEY, api_secret=LASTFM_SECRET)
        user = network.get_user(username)
        top_tracks = user.get_top_tracks(limit=15)
        
        if not top_tracks:
            return "No listening history found. Please ensure the profile is public."

        # 2. Process Tags
        tag_counts = {}
        for item in top_tracks:
            tags = item.item.get_top_tags(limit=5)
            for tag in tags:
                name = tag.item.get_name().lower()
                tag_counts[name] = tag_counts.get(name, 0) + 1
        
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)      
        tag_string = ", ".join([f"{tag} ({count})" for tag, count in sorted_tags[:15]])
        
        # 3. Initialize Groq Client
        client = Groq(api_key=GROQ_KEY)
        
        # 4. Generate Analysis using Llama 3 (70B is great for reasoning)
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a Music Psychologist. Analyze music tags using the Big Five (OCEAN) framework. "
                        "Provide a supportive report with sections for: 1. Summary, 2. The Five Pillars (OCEAN), "
                        "and 3. Emotional Regulation Style."
                    )
                },
                {
                    "role": "user",
                    "content": f"Analyze these music tags and patterns: {tag_string}"
                }
            ],
            temperature=0.7,
            max_tokens=1024,
        )
        
        return completion.choices[0].message.content

    except Exception as e:
        if "rate_limit_exceeded" in str(e).lower():
            return "🕒 Groq Rate Limit hit. Please wait a few seconds and try again."
        return f"❌ An error occurred: {str(e)}"
