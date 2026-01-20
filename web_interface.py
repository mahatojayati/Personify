import streamlit as st
from psychological_report_generation import get_musical_summary, conn

# Check if the user is already logged in via session state
if "user" not in st.session_state:
    st.session_state.user = None

# Sidebar Authentication UI
with st.sidebar:
    st.title("🔐 User Access")
    if not st.session_state.user:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Log In"):
                try:
                    # Authenticate with Supabase
                    response = conn.auth.sign_in_with_password({"email": email, "password": password})
                    st.session_state.user = response.user
                    st.rerun()
                except Exception as e:
                    st.error(f"Login failed: {e}")
        
        with col2:
            if st.button("Sign Up"):
                try:
                    conn.auth.sign_up({"email": email, "password": password})
                    st.success("Check your email for a confirmation link!")
                except Exception as e:
                    st.error(f"Sign up failed: {e}")
    else:
        st.write(f"Logged in as: **{st.session_state.user.email}**")
        if st.button("Log Out"):
            conn.auth.sign_out()
            st.session_state.user = None
            st.rerun()

st.set_page_config(page_title="Personify | Music Psychology", page_icon="🎶", layout="centered")

st.title("🎶 Musical Psychology Mirror")
st.markdown("Discover your personality through your musical DNA. Powered by GitHub Models & Supabase.")

target_user = st.text_input("Last.fm Username", placeholder="enter your username.")

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
