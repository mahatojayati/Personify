import streamlit as st
from psychological_report_generation import get_musical_summary

st.set_page_config(page_title="Personify | Music Psychology", page_icon="🧠", layout="centered")

st.title("🎶 Musical Psychology Mirror")
st.markdown("Discover your personality through your musical DNA using **Groq + Llama 3**.")

target_user = st.text_input("Last.fm Username", value="", placeholder="e.g., rj")

if st.button("Generate My AI Profile"):
    if not target_user:
        st.warning("Please enter a username.")
    else:
        with st.spinner("🚀 Groq is processing your musical profile at warp speed..."):
            report = get_musical_summary(target_user)
            st.divider()
            st.markdown(report)
            st.divider()
            st.caption("Powered by Groq Cloud & Llama 3")
