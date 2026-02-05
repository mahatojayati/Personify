import streamlit as st
import pandas as pd
from psychological_report_generation import get_musical_summary, get_recent_findings

# App Setup
st.set_page_config(page_title="Personify", page_icon="🎶", layout="centered")

st.title("🎶 Musical Psychology Mirror")

# Navigation Tabs
tab_analyze, tab_history = st.tabs(["🔍 Analyzer", "📜 History"])

with tab_analyze:
    st.markdown("### Discover your personality through your music.")
    user_input = st.text_input("Last.fm Username", placeholder="e.g., rj")

    if st.button("Generate Analysis"):
        if not user_input:
            st.warning("Please enter a username.")
        else:
            with st.spinner("🧠 AI Psychologist is thinking..."):
                report = get_musical_summary(user_input)
                st.divider()
                st.markdown(report)

with tab_history:
    st.subheader("Recent Community Profiles")
    history_data = get_recent_findings()
    
    if history_data:
        df = pd.DataFrame(history_data)
        # Displaying key columns in a table
        st.dataframe(
            df[["username", "tags_analyzed", "ocean_report"]],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No records found in the database yet.")

st.divider()
st.caption("Built with: GitHub Models (GPT-4o-mini) | Supabase | Last.fm API")
