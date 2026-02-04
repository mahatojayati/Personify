import streamlit as st
import pylast
from openai import OpenAI
from st_supabase_connection import SupabaseConnection

# 1. Initialize Connections
# Define 'conn' at the module level so web_interface.py can import it
conn = st.connection("supabase", type=SupabaseConnection)

def get_musical_summary(username):
    # Load credentials
    last_fm_key = st.secrets["LASTFM_API_KEY"]
    last_fm_secret = st.secrets["LASTFM_API_SECRET"]
    github_token = st.secrets["GITHUB_TOKEN"]

    try:
        # Last.fm Setup
        network = pylast.LastFMNetwork(api_key=last_fm_key, api_secret=last_fm_secret)
        user = network.get_user(username)
        top_tracks = user.get_top_tracks(limit=15)
        
        if not top_tracks:
            return "No public history found for this user."

        # Tag processing
        tag_counts = {}
        for item in top_tracks:
            tags = item.item.get_top_tags(limit=3)
            for tag in tags:
                name = tag.item.get_name().lower()
                tag_counts[name] = tag_counts.get(name, 0) + 1
        
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        tag_string = ", ".join([f"{t} ({c})" for t, c in sorted_tags[:10]])

        # 2. GitHub Models (OpenAI Compatible)
        client = OpenAI(
            base_url="https://models.inference.ai.azure.com",
            api_key=github_token
        )
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a Music Psychologist using the OCEAN framework."},
                {"role": "user", "content": f"Analyze these tags: {tag_string}"}
            ]
        )
        report = response.choices[0].message.content

        # 3. Supabase Insertion
        try:
            conn.table("musical_findings").insert({
                "username": username,
                "ocean_report": report,
                "tags_analyzed": tag_string
            }).execute()
        except Exception as e:
            st.warning(f"⚠️ Report generated, but data was not saved to the database: {e}")

        return report

    except Exception as e:
        return f"Error: {str(e)}"
