🎶 Personify: Musical Psychology Mirror
Personify is an AI-powered analytical tool that mirrors your inner personality through your musical DNA. By processing listening habits from Last.fm, the application utilizes GitHub Models to generate a psychological profile based on the Big Five (OCEAN) personality framework.

🚀 Key Features
Deep Listening Analysis: Fetches real-time track-level tags and frequency data via the Last.fm API.

GitHub Models Integration: Powered by Llama 3.3 via GitHub’s high-performance inference endpoint for secure, industry-standard AI analysis.

Structured Psychological Reports: Provides a comprehensive breakdown of the Five Pillars (OCEAN) and your unique Emotional Regulation Style.

Developer-First Architecture: Built with Streamlit for a fast, responsive, and secure UI.

🛠️ Tech Stack
Language: Python 3.9+

Frontend: Streamlit

AI Infrastructure: GitHub Models (OpenAI-compatible API)

Music Metadata: Pylast (Last.fm API wrapper)

Data Visualization: Pandas & Plotly

🔒 Security & Setup
To protect sensitive credentials, this project uses Streamlit Secrets. Do not upload your secrets.toml or config/ folders to public repositories.

1. Installation
Bash

git clone https://github.com/yourusername/Personify.git
cd Personify
pip install -r requirements.txt
2. Configure Secrets
Create a .streamlit/secrets.toml file in your root directory:

Ini, TOML

LASTFM_API_KEY = "your_lastfm_key"
LASTFM_API_SECRET = "your_lastfm_secret"
GITHUB_TOKEN = "your_github_personal_access_token"
Note: For GitHub Models, use a GitHub Personal Access Token (classic) with no scopes required for basic model inference.

3. Run Locally
Bash

streamlit run web_interface.py
🧠 Why GitHub Models?
Migrating from traditional endpoints to GitHub Models ensures:

Enterprise-Grade Performance: Models run on GitHub’s infrastructure, removing the need for local GPU management.

Security: Professional-grade security for your API calls and data handling.

Portfolio Impact: Demonstrates a high level of integration within the GitHub ecosystem, a key skill for modern software engineering roles and GSoC contributions.

🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request or open an issue if you have ideas for new features, such as Spotify playlist integration or advanced data visualizations.
