import streamlit as st
from psychological_report_generation import get_musical_summary

# --- Page Setup ---
st.set_page_config(
    page_title="Personify | Music Psychology",
    page_icon="🎶",
    layout="centered"
)

st.title("🎶 Musical Psychology Mirror")
st.markdown("""
    Explore your personality through your musical DNA. 
    Powered by **GitHub Models** and **Last.fm**.
""")

# --- User Input Section ---
st.subheader("Connect your Last.fm")
target_user = st.text_input("Last.fm Username", placeholder="e.g.LastFM username")

if st.button("Generate My Analysis"):
    if not target_user:
        st.warning("Please enter a username first.")
    else:
        # The spinner stays visible while the data fetches and AI processes
        with st.spinner(f"🧠 AI Psychologist is analyzing {target_user}'s listening history..."):
            report = get_musical_summary(target_user)
            
            st.divider()
            st.markdown("### 📊 Your Psychological Profile")
            st.markdown(report)
            # In your Streamlit code:
st.divider()
st.subheader("Was this report accurate?")
accuracy_rating = st.slider("Rate the psychological insight (1-5):", 1, 5)
if st.button("Submit Feedback"):
    # Save accuracy_rating to your database (MongoDB/CSV)
    st.success("Thank you! This helps improve the model's accuracy.")
            
            # --- Footer and Feedback ---
            st.divider()
            st.info("Analysis based on the Big Five (OCEAN) framework. For entertainment and self-reflection.")
            st.caption("Infrastructure: GitHub Models (GPT-4o-mini) | Data: Last.fm API")
