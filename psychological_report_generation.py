import streamlit as st
import pylast
from openai import OpenAI
from st_supabase_connection import SupabaseConnection

# Initialize Supabase Connection
conn = st.connection("supabase", type=SupabaseConnection)

def get_musical_summary(username):
    try:
        # 1. Initialize Last.fm
        network = pylast.LastFMNetwork(
            api_key=st.secrets["LASTFM_API_KEY"],
            api_secret=st.secrets["LASTFM_API_SECRET"]
        )
        user = network.get_user(username)
        
        # FAULT FIX: Increase limit to 20 for a better data sample
        top_tracks = user.get_top_tracks(limit=20)
        
        if not top_tracks:
            return "No public listening history found. Ensure the profile is public."

        # 2. Extract and count tags
        tag_counts = {}
        for item in top_tracks:
            track_tags = item.item.get_top_tags(limit=5)
            for tag in track_tags:
                name = tag.item.get_name().lower()
                tag_counts[name] = tag_counts.get(name, 0) + 1
        
        # FAULT FIX: Check if we actually found any tags
        if not tag_counts:
            return "Your top tracks don't have enough genre tags for an analysis. Try a different user."

        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        tag_string = ", ".join([f"{t} ({c})" for t, c in sorted_tags[:15]])

        # 3. GitHub Models AI Call
        client = OpenAI(
            base_url="https://models.inference.ai.azure.com",
            api_key=st.secrets["GITHUB_TOKEN"]
        )
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "You are a professional Music Psychologist. Analyze the user's personality "
                        "strictly based on the provided musical tags using the OCEAN framework. "
                        "Be specific, avoid generic advice, and provide quantitative-style insights."
                    )
                },
                {"role": "user", "content": f"Analyze these musical patterns and tags: {tag_string}"}
            ],
            temperature=0.7,
        )
        report = response.choices[0].message.content

        # 4. Save finding to Supabase
        try:
            conn.table("musical_findings").insert({
                "username": username,
                "ocean_report": report,
                "tags_analyzed": tag_string
            }).execute()
        except Exception as db_e:
            st.warning(f"⚠️ Report generated, but database sync failed: {db_e}")

        return report

    except Exception as e:
        return f"❌ Error: {str(e)}"
