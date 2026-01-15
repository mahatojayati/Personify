import streamlit as st
import pylast
from openai import OpenAI

# Load credentials
LASTAPI_KEY = st.secrets.get("LASTFM_API_KEY")
LASTFM_SECRET = st.secrets.get("LASTFM_API_SECRET")
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN")

def get_musical_summary(username):
    if not all([LASTAPI_KEY, LASTFM_SECRET, GITHUB_TOKEN]):
        return "⚠️ Configuration Error: API keys missing."

    try:
        # --- Last.fm Logic ---
        network = pylast.LastFMNetwork(api_key=LASTAPI_KEY, api_secret=LASTFM_SECRET)
        user = network.get_user(username)
        top_tracks = user.get_top_tracks(limit=15)
        
        if not top_tracks:
            return f"No listening history found for user '{username}'."

        tag_counts = {}
        for item in top_tracks:
            tags = item.item.get_top_tags(limit=3)
            for tag in tags:
                name = tag.item.get_name().lower()
                tag_counts[name] = tag_counts.get(name, 0) + 1
        
        tag_string = ", ".join([f"{tag} ({count})" for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]])
        
        # --- GitHub Models Logic ---
        client = OpenAI(
            base_url="https://models.inference.ai.azure.com",
            api_key=GITHUB_TOKEN,
        )
        
        # CHANGED: Using gpt-4o-mini for better reliability and quota
        response = client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=[
                {
                    "role": "system", 
                    "content": "You are a Music Psychologist. Analyze these tags using the OCEAN personality framework."
                },
                {"role": "user", "content": f"Tags: {tag_string}"}
            ],
            temperature=0.7,
        )
        
        return response.choices[0].message.content

    except Exception as e:
        # Catch the "Unknown model" error specifically to give feedback
        if "unknown_model" in str(e):
            return "❌ Model Error: The selected model ID is incorrect. Try 'gpt-4o-mini' or 'meta/llama-3.3-70b'."
        return f"❌ Technical Error: {str(e)}"
