import streamlit as st
import pylast
from google import genai
from google.genai import types

import streamlit as st
import tomllib  # Or 'import toml' if on Python < 3.11
import os

# Manual path to your secrets
secrets_path = os.path.join("config", "secrets.toml")

if os.path.exists(secrets_path):
    with open(secrets_path, "rb") as f:
        config = tomllib.load(f)
    LASTAPI_KEY = config.get("LASTFM_API_KEY")
    LASTFM_SECRET = config.get("LASTFM_API_SECRET")
    GEMINI_KEY = config.get("GEMINI_API_KEY")
else:
    st.error("Could not find config/secrets.toml")
    
    try:
        network = pylast.LastFMNetwork(api_key=LASTAPI_KEY, api_secret=LASTFM_SECRET)
        client = genai.Client(api_key=GEMINI_KEY)
        
        user = network.get_user(username)
        top_tracks = user.get_top_tracks(limit=15)
        
        if not top_tracks:
            return "No listening history found for this user. Please ensure the profile is public."

        tag_counts = {}
        for item in top_tracks:
            # item.item refers to the Track object in pylast
            tags = item.item.get_top_tags(limit=5)
            for tag in tags:
                name = tag.item.get_name().lower()
                tag_counts[name] = tag_counts.get(name, 0) + 1
        
        # Sort and format top tags for the prompt
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)      
        tag_string = ", ".join([f"{tag} ({count})" for tag, count in sorted_tags[:15]])
        
        # Generate the AI report
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(
                system_instruction=(
                    "You are a Music Psychologist. Analyze music tags using the Big Five (OCEAN) framework. "
                    "Provide a supportive, insightful report with clear sections for: "
                    "1. Summary, 2. The Five Pillars (OCEAN Scores), and 3. Emotional Regulation Style."
                ),
                temperature=0.7,
            ),
            contents=f"Analyze these music tags and listening patterns: {tag_string}"
        )
        return response.text

    except pylast.PyLastError as e:
        return f"Last.fm Error: {e}. Check if the username exists."
    except Exception as e:
        return f"An error occurred: {str(e)}"
