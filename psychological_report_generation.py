import streamlit as st
import pylast
from openai import OpenAI
from st_supabase_connection import SupabaseConnection

# Initialize Supabase Connection
conn = st.connection("supabase", type=SupabaseConnection)

def get_musical_summary(username):
    """Fetches music data, generates a report via GitHub AI, and saves to Supabase."""
    try:
        # 1. Initialize Last.fm
        network = pylast.LastFMNetwork(
            api_key=st.secrets["LASTFM_API_KEY"],
            api_secret=st.secrets["LASTFM_API_SECRET"]
        )
        user = network.get_user(username)
        top_tracks = user.get_top_tracks(limit=5)
        
        if not top_tracks:
            return "No public listening history found. Is the username correct and public?"

        # 2. Extract and count tags (The "Musical DNA")
        tag_counts = {}
        for item in top_tracks:
            # item.item is the pylast Track object
            track_tags = item.item.get_top_tags(limit=3)
            for tag in track_tags:
                name = tag.item.get_name().lower()
                tag_counts[name] = tag_counts.get(name, 0) + 1
        
        # Sort and format tags for the prompt
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        tag_string = ", ".join([f"{t} ({c})" for t, c in sorted_tags[:12]])

        # 3. GitHub Models AI Call (OpenAI SDK)
        client = OpenAI(
            base_url="https://models.inference.ai.azure.com",
            api_key=st.secrets["GITHUB_TOKEN"]
        )
        
        # We explicitly include the tag_string in the message
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "You are a professional Music Psychologist. Analyze the user's personality "
                        "using the Big Five (OCEAN) framework based on their music tags. "
                        "Structure your report clearly ."
                        "Provide a proper conclusion based on analyses."
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

def get_recent_findings(limit=5):
    """Fetches history for the History tab."""
    try:
        response = conn.table("musical_findings").select("*").order("id", desc=True).limit(limit).execute()
        return response.data
    except Exception:
        return []
