# Personify
# 🎶 Musical Psychology Mirror

An AI-powered application that analyzes your Last.fm listening habits to generate a psychological profile based on the **Big Five (OCEAN) Personality Traits**.



[Image of the Big Five Personality Traits (OCEAN)]


## ✨ Features
- **Last.fm Integration**: Fetches your top tracks and associated genre tags.
- **Gemini 2.0 Flash**: Uses advanced LLM reasoning to map musical patterns to psychological insights.
- **OCEAN Framework**: Provides a breakdown of Openness, Conscientiousness, Extraversion, Agreeableness, and Neuroticism.
- **Secure Architecture**: Built for Streamlit Cloud with hidden API secrets.

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- A [Last.fm API Key](https://www.last.fm/api/account/create)
- A [Google Gemini API Key](https://aistudio.google.com/)

### Installation
1. **Clone the repository:**
   ```bash
   git clone [https://github.com/yourusername/musical-psychology-mirror.git](https://github.com/yourusername/musical-psychology-mirror.git)
   cd musical-psychology-mirror

2. Install Dependencies
   pip install -r requirements.txt

3. Set up Secrets: Create a .streamlit/secrets.toml file and add your credentials:
LASTFM_API_KEY = "your_key"
LASTFM_API_SECRET = "your_secret"
GEMINI_API_KEY = "your_gemini_key"

4. Run the App:
   Streamlit - run web_interface.py

 🛠️ Tech Stack
Frontend: Streamlit

Music Data: pylast (Last.fm API wrapper)

AI Model: Google Gemini 2.0 Flash

🔒 Security Note
This project uses .gitignore to prevent secrets.toml from being uploaded to GitHub.
