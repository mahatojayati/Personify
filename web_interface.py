import streamlit as st
from psychological_report_generation import get_musical_summary

# --- Page Configuration ---
st.set_page_config(
    page_title="Personify | Music Psychology",
    page_icon="🎶",
    layout="centered"
)

# --- UI Header ---
st.title("🎶 Musical Psychology Mirror")
st.markdown("""
    Explore your personality through your musical DNA. 
    This tool analyzes your Last.fm listening habits and uses **GitHub Models** to generate a psychological profile based on the **OCEAN framework**.
""")

# --- User Input Section ---
st.subheader("Connect your Last.fm")
target_user = st.text_input("Last.fm Username", placeholder="Enter your username (e.g., rj)")

# --- Analysis Logic ---
if st.button("Generate My Analysis"):
    if not target_user:
        st.warning("Please enter a Last.fm username to proceed.")
    else:
        # Display a spinner while fetching data and calling the AI
        with st.spinner(f"🧠 AI Psychologist is analyzing {target_user}'s listening history..."):
            # Call the backend logic which handles Last.fm, GitHub Models, and Supabase
            report = get_musical_summary(target_user)
            
            st.divider()
            st.markdown("### 📊 Your Psychological Profile")
            st.markdown(report)
            
            # --- Footer and Disclaimer ---
            st.divider()
            st.info("Analysis based on the Big Five (OCEAN) framework. For entertainment and self-reflection.")
            st.caption("Infrastructure: GitHub Models (GPT-4o-mini) | Data: Last.fm API | Database: Supabase")
