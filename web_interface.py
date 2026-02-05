import streamlit as st
import pandas as pd
from psychological_report_generation import get_musical_summary, get_recent_findings

st.set_page_config(page_title="Personify", page_icon="🎶", layout="centered")

st.title("🎶 Musical Psychology Mirror")

# Navigation
tab_main, tab_history = st.tabs(["🔍 Analyze", "📜 Public History"])

with tab_main:
    user_input = st.text_input("Enter Last.fm Username", placeholder="e.g., rj")
    
    if st.button("Generate Report"):
        if not user_input:
            st.warning("Username is required!")
        else:
            with st.spinner("🧠 AI Psychologist is reviewing your data..."):
                result = get_musical_summary(user_input)
                st.divider()
                st.markdown(result)

with tab_history:
    st.subheader("Recent Community Findings")
    history_data = get_recent_findings()
    
    if history_data:
        df = pd.DataFrame(history_data)
        st.dataframe(
            df[["username", "tags_analyzed", "ocean_report"]],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No records found yet.")

st.divider()
st.caption("Infrastructure: GitHub Models (GPT-4o-mini) | DB: Supabase | Data: Last.fm")
