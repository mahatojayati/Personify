import streamlit as st
import pylast
from openai import OpenAI
from st_supabase_connection import SupabaseConnection

# Initialize Supabase Connection
# Ensure your secrets.toml has the [connections.supabase] section
conn = st.connection("supabase", type=SupabaseConnection)

def get_recent_findings():
    """
    Fetches the 5 most recent reports from Supabase.
    This is the function your web_interface.py was failing to find.
    """
    try:
        # Fetch top 5 recent entries. 
        # Make sure your Supabase table has an 'id' or 'created_at' column.
        response = conn.table("musical_findings").select("*").order("id", desc=True).limit(5).execute()
        return response.data
    except Exception as e:
        # Log to console so you can see it in your terminal
        print(f"Database Fetch Error: {e}")
        return []

def get_musical_summary(username):
    """
    Generates a psychological report based on Last.fm listening history.
    """
    # 1. Input Sanitization
    username = username.strip()
    
    try:
        # 2. Initialize Last.fm with specific error handling
        try:
            network = pylast.LastFMNetwork(
                api_key=st.secrets["LASTFM_API_KEY"],
                api_secret=st.secrets["LASTFM_API_SECRET"]
            )
            user = network.get_user(username)
            # Force an API call to validate user existence immediately
            top_tracks = user.get_top_tracks(limit=20)
        except pylast.WSError as lastfm_err:
            if "User not found" in str(lastfm_err):
                return f"❌ User '{username}' not found on Last.fm. Check the spelling."
            elif "Invalid API key" in str(lastfm_err):
                return "❌ Configuration Error: Invalid Last.fm API Key."
            else:
                return f"❌ Last.fm API Error: {lastfm_err}"
        except Exception as net_err:
             return f"❌ Network/Connection Error: {str(net_err)}"
        
        if not top_tracks:
            return "⚠️ No public listening history found. The user might be new or private."

        # 3. Extract and count tags
        tag_counts = {}
        for item in top_tracks:
            # Safety check: obscure tracks might return None for tags
            track_tags = item.item.get_top_tags(limit=5)
            if track_tags:
                for tag in track_tags:
                    name = tag.item.get_name().lower()
                    tag_counts[name] = tag_counts.get(name, 0) + 1
        
        if not tag_counts:
            return "⚠️ Your top tracks don't have enough genre tags for a psychological analysis."

        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        # Limit to top 15 to keep prompt concise
        tag_string = ", ".join([f"{t} ({c})" for t, c in sorted_tags[:15]])

        # 4. GitHub Models AI Call
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
                            "Provide a structured report including: "
                            "Dominant Traits, Emotional Regulation Style, and a Suggested Activity. "
                            "Be direct and professional."
                        )
                    },
                    {"role": "user", "content": f"Analyze these musical patterns and tags: {tag_string}"}
                ],
                temperature=0.7,
            )
            report = response.choices[0].message.content
        except Exception as ai_e:
            return f"❌ AI Generation Error: {str(ai_e)}"

        # 5. Save finding to Supabase
        try:
            conn.table("musical_findings").insert({
                "username": username,
                "ocean_report": report,
                "tags_analyzed": tag_string
            }).execute()
        except Exception as db_e:
            st.warning(f"⚠️ Report generated, but database sync failed. Check your Supabase table permissions.")
            print(f"DB Insert Error: {db_e}")

        return report

    except Exception as e:
        return f"❌ Critical Error: {str(e)}"
