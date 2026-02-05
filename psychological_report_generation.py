import streamlit as st
import pylast
from openai import OpenAI
from st_supabase_connection import SupabaseConnection

# Initialize Supabase Connection
# Ensure your secrets.toml has the [connections.supabase] section or SUPABASE_URL/KEY set
conn = st.connection("supabase", type=SupabaseConnection)

def get_recent_findings():
    """
    Fetches the 5 most recent reports from the Supabase database.
    """
    try:
        # Query the table, order by 'created_at' descending, and limit to 5
        # Note: Ensure your table has a 'created_at' column or remove the .order()
        response = conn.table("musical_findings").select("*").order("id", desc=True).limit(5).execute()
        return response.data
    except Exception as e:
        st.error(f"Database Error: {e}")
        return []

def get_musical_summary(username):
    """
    Generates a psychological report based on Last.fm listening history.
    """
    # Sanitize input
    username = username.strip()
    
    try:
        # 1. Initialize Last.fm
        try:
            network = pylast.LastFMNetwork(
                api_key=st.secrets["LASTFM_API_KEY"],
                api_secret=st.secrets["LASTFM_API_SECRET"]
            )
            user = network.get_user(username)
            # Force a call to check if user exists/API is working
            top_tracks = user.get_top_tracks(limit=20)
        except pylast.WSError as lastfm_err:
            if "User not found" in str(lastfm_err):
                return f"❌ User '{username}' not found on Last.fm."
            elif "Invalid API key" in str(lastfm_err):
                return "❌ Configuration Error: Invalid Last.fm API Key."
            else:
                return f"❌ Last.fm API Error: {lastfm_err}"
        
        if not top_tracks:
            return "⚠️ No public listening history found. The user might be new or private."

        # 2. Extract and count tags
        tag_counts = {}
        for item in top_tracks:
            # Handle potential missing tags for obscure songs
            track_tags = item.item.get_top_tags(limit=5)
            if track_tags:
                for tag in track_tags:
                    name = tag.item.get_name().lower()
                    tag_counts[name] = tag_counts.get(name, 0) + 1
        
        if not tag_counts:
            return "⚠️ Your top tracks don't have enough genre tags for a psychological analysis."

        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        # Limit to top 10 tags to save token space and reduce noise
        tag_string = ", ".join([f"{t} ({c})" for t, c in sorted_tags[:10]])

        # 3. GitHub Models AI Call
        try:
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
                            "Provide a structured report with: "
                            "1. **Dominant Traits** (High/Low O-C-E-A-N) "
                            "2. **Emotional Regulation Style** "
                            "3. **Suggested Activity** for this personality type. "
                            "Be concise and professional."
                        )
                    },
                    {"role": "user", "content": f"Analyze these musical patterns and tags: {tag_string}"}
                ],
                temperature=0.7,
            )
            report = response.choices[0].message.content
        except Exception as ai_e:
            return f"❌ AI Generation Error: {str(ai_e)}"

        # 4. Save finding to Supabase
        try:
            conn.table("musical_findings").insert({
                "username": username,
                "ocean_report": report,
                "tags_analyzed": tag_string
            }).execute()
        except Exception as db_e:
            # We don't return here because we still want to show the user the report
            # just warn them that history wasn't saved.
            st.warning(f"⚠️ Report generated, but history sync failed: {db_e}")

        return report

    except Exception as e:
        return f"❌ Unexpected Error: {str(e)}"
