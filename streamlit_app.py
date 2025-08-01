import streamlit as st
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
]


def get_flow() -> Flow:
    return Flow.from_client_config(
        {
            "web": {
                "client_id": st.secrets["google"]["client_id"],
                "client_secret": st.secrets["google"]["client_secret"],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=SCOPES,
        redirect_uri=st.secrets["google"]["redirect_uri"],
    )


def creds_to_dict(creds: Credentials):
    return {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": creds.scopes,
    }


def get_credentials() -> Credentials | None:
    if "credentials" not in st.session_state:
        return None
    creds = Credentials(**st.session_state.credentials)
    if not creds.valid and creds.refresh_token:
        creds.refresh(Request())
        st.session_state.credentials = creds_to_dict(creds)
    return creds


def get_youtube_service():
    creds = get_credentials()
    if not creds:
        return None
    return build("youtube", "v3", credentials=creds)


st.set_page_config(page_title="YouTube Insights Tool")

st.title("YouTube Insights Tool")

# Ensure OAuth credentials are available
if "google" not in st.secrets:
    st.error("Google OAuth credentials missing in `secrets.toml`.")
    st.stop()

# Process OAuth2 redirect
query_params = st.query_params
if "code" in query_params and "state" in query_params:
    if (
        "state" in st.session_state
        and st.session_state["state"] == query_params["state"][0]
    ):
        flow = get_flow()
        flow.fetch_token(code=query_params["code"][0])
        st.session_state.credentials = creds_to_dict(flow.credentials)
        st.experimental_rerun()

creds = get_credentials()

if creds:
    st.success("Authenticated with Google")
    if st.button("Logout"):
        del st.session_state.credentials
        st.experimental_rerun()
    youtube = get_youtube_service()
    if youtube:
        # Example request listing user's channels
        channels = (
            youtube.channels()
            .list(part="snippet,statistics", mine=True)
            .execute()
        )
        st.json(channels)
else:
    if st.button("Login with Google"):
        flow = get_flow()
        auth_url, state = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent",
        )
        st.session_state["state"] = state
        st.markdown(f"[Continue here]({auth_url})")
        st.stop()
