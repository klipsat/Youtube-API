# YT Insights App

This Streamlit app allows users to analyze YouTube videos using YouTube Data and Analytics APIs.

## Features

- OAuth login
- Key metrics extraction
- Clean UI for creators and marketers

## Deploy on Streamlit

1. Upload this repo to GitHub
2. Go to https://streamlit.io/cloud
3. Connect GitHub and deploy `streamlit_app.py`
4. Set the following fields in `.streamlit/secrets.toml`:

```toml
[google]
client_id = "YOUR_CLIENT_ID"
client_secret = "YOUR_CLIENT_SECRET"
redirect_uri = "https://your-app-name.streamlit.app"
```

5. Install dependencies locally with `pip install -r requirements.txt` if you
   run the app outside Streamlit Cloud.

## Notes

- The OAuth client ID and secret are kept private in `.streamlit/secrets.toml`.
- Users authenticate with their own Google accounts during runtime.
- Login credentials are stored in `st.session_state` and can be cleared with the **Logout** button.
