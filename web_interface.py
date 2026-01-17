import streamlit as st
from psychological_report_generation import get_musical_summary

st.set_page_config(page_title="Personify | Music Psychology", page_icon="🎶", layout="centered")

st.title("🎶 Musical Psychology Mirror")
st.markdown("Discover your personality through your musical DNA. Powered by GitHub Models & Supabase.")

target_user = st.text_input("Last.fm Username", placeholder="e.g., rj")

if st.button("Generate My Analysis"):
    if not target_user:
        st.warning("Please enter a username.")
    else:
        with st.spinner("🧠 Consulting the AI Music Psychologist..."):
            report = get_musical_summary(target_user)
            st.divider()
            st.markdown("### 📊 Your Psychological Profile")
            st.markdown(report)
            st.divider()
            st.caption("Infrastructure: GitHub Models | Database: Supabase")
