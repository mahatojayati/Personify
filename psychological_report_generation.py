import streamlit as st
import pylast
from openai import OpenAI
from st_supabase_connection import SupabaseConnection

try:
    conn = st.connection("supabase", type=SupabaseConnection)
    # Simple check to fetch one row from your table
    test = conn.table("musical_findings").select("*").limit(1).execute()
    st.success("✅ Connection Successful!")
except Exception as e:
    st.error(f"❌ Connection still failing: {e}")

# Load credentials from Streamlit Secrets
LASTAPI_KEY = st.secrets["LASTFM_API_KEY"]
LASTFM_SECRET = st.secrets["LASTFM_API_SECRET"]
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]

# Initialize connections
network = pylast.LastFMNetwork(api_key=LASTAPI_KEY, api_secret=LASTFM_SECRET)
conn = st.connection("supabase", type=SupabaseConnection)

def get_musical_summary(username):
    """Fetches user tags and generates a report via GitHub Models."""
    try:
        # 1. Fetch data from Last.fm
        user = network.get_user(username)
        top_tracks = user.get_top_tracks(limit=15)
        
        if not top_tracks:
            return "No listening history found. Ensure the profile is public."

        tag_counts = {}
        for item in top_tracks:
            track_tags = item.item.get_top_tags(limit=3)
            for tag in track_tags:
                name = tag.item.get_name().lower()
                tag_counts[name] = tag_counts.get(name, 0) + 1
        
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)      
        tag_string = ", ".join([f"{tag} ({count})" for tag, count in sorted_tags[:10]])
        
        # 2. Generate AI Report via GitHub Models (OpenAI Client)
        client = OpenAI(
            base_url="https://models.inference.ai.azure.com",
            api_key=GITHUB_TOKEN,
        )
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a Music Psychologist. Analyze these tags using the Big Five (OCEAN) framework."},
                {"role": "user", "content": f"Analyze these tags: {tag_string}"}
            ],
            temperature=0.7,
        )
        report_text = response.choices[0].message.content

        # 3. Store Findings in Supabase
        try:
            data = {
                "username": username,
                "ocean_report": report_text,
                "tags_analyzed": tag_string
            }
            conn.table("musical_findings").insert(data).execute()
        except Exception as db_e:
            st.warning(f"⚠️ Report generated, but data was not saved to the database: {db_e}")

        return report_text

    except Exception as e:
        return f"An error occurred: {str(e)}"
        def get_recent_findings(limit=10):
    """Fetches the most recent psychological reports from Supabase."""
    try:
        # Query the table using the st.connection interface
        # We set ttl="1m" to cache results for 1 minute to save on API calls
        response = conn.table("musical_findings").select("*").order("created_at", desc=True).limit(limit).execute()
        return response.data
    except Exception as e:
        st.error(f"Could not retrieve history: {e}")
        return []
