import streamlit as st
from psychological_report_generation import get_musical_summary

# Page Configuration
st.set_page_config(page_title="Musical Psychology Mirror", page_icon="🎶", layout="centered")

st.title("🎶 Musical Psychology Mirror")
st.markdown("""
    Discover your personality through your musical DNA. 
    Enter your Last.fm username below to generate an AI-powered psychological profile.
""")

# User Input
target_user = st.text_input("Last.fm Username", value="", placeholder="Enter username (e.g., rj)")

if st.button("Generate Analysis"):
    if not target_user:
        st.warning("Please enter a Last.fm username to proceed.")
    else:
        with st.spinner("🧠 Consulting the AI Music Psychologist..."):
            # Call the analysis function
            report = get_musical_summary(target_user)
            
            st.divider()
            st.markdown("### 📊 Your Psychological Profile")
            st.markdown(report)
            
            st.divider()
            st.caption("Disclaimer: This tool is for entertainment and self-reflection purposes.")
