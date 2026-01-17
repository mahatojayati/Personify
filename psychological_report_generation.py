import streamlit as st
import pylast
from openai import OpenAI
from st_supabase_connection import SupabaseConnection

# --- Configuration: Load Credentials from Streamlit Secrets ---
# Ensure these keys are set in your .streamlit/secrets.toml file
LASTAPI_KEY = st.secrets.get("LASTFM_API_KEY")
LASTFM_SECRET = st.secrets.get("LASTFM_API_SECRET")
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN")

# --- Initialize Connections ---
# Initialize Supabase Connection
conn = st.connection("supabase", type=SupabaseConnection)

def save_to_supabase(username, report, tags):
    """Attempts to insert findings into the Supabase database."""
    try:
        data = {
            "username": username,
            "ocean_report": report,
            "tags_analyzed": tags
        }
        conn.table("musical_findings").insert(data).execute()
        return True
    except Exception as e:
        # We catch the error here to allow for the fallback warning in the main logic
        st.sidebar.error(f"Database Sync Error: {e}")
        return False

def get_musical_summary(username):
    """
    Fetches user data from Last.fm, generates a report via GitHub Models,
    and stores the result in Supabase.
    """
    if not all([LASTAPI_KEY, LASTFM_SECRET, GITHUB_TOKEN]):
        return "⚠️ Configuration Error: API keys missing from secrets."

    try:
        # 1. Last.fm Data Extraction
        network = pylast.LastFMNetwork(api_key=LASTAPI_KEY, api_secret=LASTFM_SECRET)
        user = network.get_user(username)
        top_tracks = user.get_top_tracks(limit=15)
        
        if not top_tracks:
            return f"No listening history found for user '{username}'."

        # FIX: Corrected the tag counting logic
        tag_counts = {}
        for item in top_tracks:
            # Fetches tags for each specific track
            track_tags = item.item.get_top_tags(limit=3)
            for tag in track_tags:
                name = tag.item.get_name().lower()
                tag_counts[name] = tag_counts.get(name, 0) + 1
        
        # Format the most frequent tags for the LLM
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)      
        tag_string = ", ".join([f"{tag} ({count})" for tag, count in sorted_tags[:10]])
        
        # 2. GitHub Models Logic (OpenAI Compatible)
        client = OpenAI(
            base_url="https://models.inference.ai.azure.com",
            api_key=GITHUB_TOKEN,
        )
        
        response = client.chat.completions.create(
            model="gpt-4o-mini", # Highly efficient for psychological profiling
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "You are a professional Music Psychologist. "
                        "Analyze the provided music tags using the Big Five (OCEAN) framework. "
                        "Provide a supportive report with sections for: 1. Summary, "
                        "2. The Five Pillars (OCEAN), and 3. Emotional Regulation Style."
                    )
                },
                {"role": "user", "content": f"Analyze these musical patterns: {tag_string}"}
            ],
            temperature=0.7,
        )
        
        report_text = response.choices[0].message.content

        # 3. Supabase Integration with Fallback Warning
        # Attempt to store the data
        storage_success = save_to_supabase(username, report_text, tag_string)
        
        if not storage_success:
            st.warning("⚠️ Report generated successfully, but your data didn't get stored in the database.")

        return report_text

    except pylast.PyLastError as e:
        return f"❌ Last.fm Error: {e}. Please check the username."
    except Exception as e:
        return f"❌ Technical Error: {str(e)}"
