import streamlit as st
import pylast
from google import genai
from google.genai import types

# Load credentials from Streamlit Secrets
LASTAPI_KEY = st.secrets["LASTFM_API_KEY"]
LASTFM_SECRET = st.secrets["LASTFM_API_SECRET"]
GEMINI_KEY = st.secrets["GEMINI_API_KEY"]

# Initialize clients
network = pylast.LastFMNetwork(api_key=LASTAPI_KEY, api_secret=LASTFM_SECRET)
client = genai.Client(api_key=GEMINI_KEY)

def get_musical_summary(username):
    """Fetches user tags and generates a psychological report via Gemini."""
    try:
        user = network.get_user(username)
        # Fetching top 15 tracks to get a broader data sample
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
    
    import streamlit as st
from st_supabase_connection import SupabaseConnection

# Initialize Supabase Connection
# type=SupabaseConnection handles the st.secrets["connections.supabase"] automatically
conn = st.connection("supabase", type=SupabaseConnection)

def save_to_supabase(username, report, tags):
    """Inserts the generated report into the Supabase database."""
    try:
        data = {
            "username": username,
            "ocean_report": report,
            "tags_analyzed": tags
        }
        # Insert data into the 'musical_findings' table
        conn.table("musical_findings").insert(data).execute()
        return True
    except Exception as e:
        st.error(f"Database Error: {e}")
        return False

# Updated Analysis Function (Simplified logic)
def get_musical_summary(username):
    # ... (Your existing Last.fm and GitHub Models logic here) ...
    report = response.choices[0].message.content
    
    # Save finding to database
    save_to_supabase(username, report, tag_string)
    
    return report
