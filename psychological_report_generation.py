import streamlit as st
import pylast
from google import genai
from google.genai import types

# Accessing keys via Streamlit's secrets management
# This ensures keys are not hardcoded in the script
LASTAPI_KEY = st.secrets.get("LASTFM_API_KEY")
LASTFM_SECRET = st.secrets.get("LASTFM_API_SECRET")
GEMINI_KEY = st.secrets.get("GEMINI_API_KEY")

def get_musical_summary(username):
    """Fetches user tags and generates a psychological report via Gemini."""
    if not all([LASTAPI_KEY, LASTFM_SECRET, GEMINI_KEY]):
        return "⚠️ Configuration Error: API keys not found in Streamlit Secrets."

    try:
        # Initialize Last.fm network
        network = pylast.LastFMNetwork(api_key=LASTAPI_KEY, api_secret=LASTFM_SECRET)
        # Initialize Gemini client
        client = genai.Client(api_key=GEMINI_KEY)
        
        user = network.get_user(username)
        # Fetching top 15 tracks to provide a broader sample for analysis
        top_tracks = user.get_top_tracks(limit=15)
        
        if not top_tracks:
            return "No listening history found. Please ensure the Last.fm profile is public."

        tag_counts = {}
        for item in top_tracks:
            # Fetches top 5 tags for each individual track
            tags = item.item.get_top_tags(limit=5)
            for tag in tags:
                name = tag.item.get_name().lower()
                tag_counts[name] = tag_counts.get(name, 0) + 1
        
        # Format the most frequent tags for the prompt
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)      
        tag_string = ", ".join([f"{tag} ({count})" for tag, count in sorted_tags[:15]])
        
        # Generate the structured report using Gemini 2.0 Flash
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(
                system_instruction=(
                    "You are a Music Psychologist. Analyze music tags using the Big Five (OCEAN) framework. "
                    "Provide a supportive, insightful report with clear sections for: "
                    "1. Summary, 2. The Five Pillars (OCEAN), and 3. Emotional Regulation Style."
                ),
                temperature=0.7,
            ),
            contents=f"Analyze these music tags and listening patterns: {tag_string}"
        )
        return response.text

    except pylast.PyLastError as e:
        return f"Last.fm API Error: {e}. Please verify the username or API Shared Secret."
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"
