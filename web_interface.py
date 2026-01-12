import streamlit as st
import pandas as pd
from psychological_report_generation import get_musical_summary

# Page Configuration
st.set_page_config(page_title="Musical Psychology Mirror", page_icon="🎶", layout="centered")

st.title("🎶 Musical Psychology Mirror")
st.markdown("""
    Explore the depths of your personality through your music. 
    Enter your Last.fm username below to generate an AI-powered psychological profile.
""")

# User Input
target_user = st.text_input("Last.fm Username", value="", placeholder="e.g., rj")

if st.button("Generate My Analysis"):
    if not target_user:
        st.warning("Please enter a valid Last.fm username first.")
    else:
        with st.spinner("🧠 Analyzing your musical DNA..."):
            report = get_musical_summary(target_user)
            
            st.divider()
            st.markdown("### 📊 Your Psychological Report")
            st.markdown(report)
            
            st.divider()
            st.caption("Disclaimer: This tool uses AI to interpret musical tastes based on the OCEAN framework. It is for entertainment and self-reflection purposes.")