import streamlit as st
import pandas as pd
from psychological_report_generation import get_musical_summary, get_recent_findings

# Page Configuration
st.set_page_config(page_title="Personify | Music Psychology", page_icon="🎶", layout="centered")

st.title("🎶 Musical Psychology Mirror")

# --- Create Tabs for Navigation ---
tab1, tab2 = st.tabs(["🔍 Analyze New User", "📜 Public History"])

with tab1:
    st.markdown("### Discover your personality through your music.")
    target_user = st.text_input("Last.fm Username", placeholder="e.g., rj")

    if st.button("Generate My Analysis"):
        if not target_user:
            st.warning("Please enter a valid Last.fm username.")
        else:
            with st.spinner("🧠 Analyzing musical DNA..."):
                report = get_musical_summary(target_user)
                st.divider()
                st.markdown(report)

with tab2:
    st.markdown("### Recent Public Profiles")
    # Fetch data from Supabase via the backend function
    history_data = get_recent_findings()
    
    if history_data:
        # Convert to a DataFrame for better display
        df = pd.DataFrame(history_data)
        
        # Clean up column names for the user
        df = df.rename(columns={
            "username": "Last.fm User",
            "ocean_report": "AI Report",
            "tags_analyzed": "Musical DNA",
            "created_at": "Analyzed On"
        })
        
        # Display as an interactive dataframe
        st.dataframe(
            df[["Last.fm User", "Musical DNA", "AI Report", "Analyzed On"]],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No public history found yet. Be the first to generate a report!")

st.divider()
st.caption("Infrastructure: GitHub Models | Database: Supabase | Data: Last.fm")
