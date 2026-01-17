import streamlit as st
import pylast
from openai import OpenAI
import streamlit as st
from st_supabase_connection import SupabaseConnection

# Initialize Supabase Connection
# This automatically looks for [connections.supabase] in your secrets.toml
conn = st.connection("supabase", type=SupabaseConnection)
# Load credentials
LASTAPI_KEY = st.secrets.get("LASTFM_API_KEY")
LASTFM_SECRET = st.secrets.get("LASTFM_API_SECRET")
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN")

def get_musical_summary(username):
    if not all([LASTAPI_KEY, LASTFM_SECRET, GITHUB_TOKEN]):
        return "⚠️ Configuration Error: API keys missing."
def get_musical_summary(username):
    # ... (Existing Last.fm data fetching logic) ...

    # 3. Call AI to generate psychological report
    response = client.models.generate_content(
        model="gemini-2.0-flash", # Fixed parameter name
        config=types.GenerateContentConfig(
            system_instruction="Analyze music tags using the Big Five (OCEAN) framework.",
            temperature=0.7,
        ),
        contents=f"Analyze these music tags: {tag_string}" # Fixed parameter name
    )
    
    report_text = response.text

    # --- NEW SUPABASE LOGIC STARTS HERE ---
    try:
        data_to_save = {
            "username": username,
            "ocean_report": report_text,
            "tags_analyzed": tag_string
        }
        # Insert the findings into your 'musical_findings' table
        conn.table("musical_findings").insert(data_to_save).execute()
    except Exception as e:
        st.error(f"Failed to save to database: {e}")
    # --- NEW SUPABASE LOGIC ENDS HERE ---

    return report_text
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
