# 🎶 Musical Psychology Mirror (Personify)

An AI-driven application that interprets Last.fm listening habits through the lens of the **Big Five (OCEAN)** personality framework.

## ✨ Features
- **Data-Driven**: Analyzes track-level genre tags from Last.fm.
- **Advanced AI**: Uses **Gemini 2.0 Flash** for high-reasoning psychological profiling.
- **Secure**: Implements Streamlit Secrets to keep API keys private.

## 🚀 Setup Instructions

1. **Clone the Project**:
   ```bash
   git clone [https://github.com/yourusername/personify.git](https://github.com/yourusername/personify.git)
   cd personify

2. Configure Secrets: Since .streamlit/ is hidden, create it via terminal:

Bash

mkdir .streamlit
touch .streamlit/secrets.toml 

3. Install & Run:

Bash

pip install -r requirements.txt
streamlit run web_interface.py

4. 🧠 The Framework
The analysis maps music to the OCEAN model:

Openness to experience

Conscientiousness

Extraversion

Agreeableness

Neuroticism
