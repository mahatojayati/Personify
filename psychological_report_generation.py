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
