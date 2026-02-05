import streamlit as st
import pylast
from openai import OpenAI
from st_supabase_connection import SupabaseConnection

# Initialize connections
# This pulls directly from your [connections.supabase] secrets block
conn = st.connection("supabase", type=SupabaseConnection)

def get_musical_summary(username):
    """Fetches music data and generates a psychological report."""
    try:
        # 1. Setup Last.fm
        network = pylast.LastFMNetwork(
            api_key=st.secrets["LASTFM_API_KEY"],
            api_secret=st.secrets["LASTFM_API_SECRET"]
        )
        user = network.get_user(username)
        top_tracks = user.get_top_tracks(limit=15)
        
        if not top_tracks:
            return "No public listening history found for this user."

        # 2. Extract and count tags
        tag_counts = {}
        for item in top_tracks:
            track_tags = item.item.get_top_tags(limit=3)
            for tag in track_tags:
                name = tag.item.get_name().lower()
                tag_counts[name] = tag_counts.get(name, 0) + 1
        
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        tag_string = ", ".join([f"{t} ({c})" for t, c in sorted_tags[:10]])

        # 3. GitHub Models AI Generation
        client = OpenAI(
            base_url="https://models.inference.ai.azure.com",
            api_key=st.secrets["GITHUB_TOKEN"]
        )
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional Music Psychologist using the OCEAN framework."},
                {"role": "user", "content": f"Analyze these musical tags: {tag_string}"}
            ]
        )
        report = response.choices[0].message.content

        # 4. Save to Supabase
        try:
            conn.table("musical_findings").insert({
                "username": username,
                "ocean_report": report,
                "tags_analyzed": tag_string
            }).execute()
        except Exception as db_e:
            st.warning(f"⚠️ Report generated, but database save failed: {db_e}")

        return report

    except Exception as e:
        return f"❌ Error: {str(e)}"

def get_recent_findings(limit=5):
    """Retrieves the latest analysis reports."""
    try:
        response = conn.table("musical_findings").select("*").order("id", desc=True).limit(limit).execute()
        return response.data
    except:
        return []
