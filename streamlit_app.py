import streamlit as st
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import os

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

# Process OAuth2 redirect using query_params
query_params = st.query_params

if "code" in query_params and "state" in query_params:
    if (
        "state" in st.session_state
        and st.session_state["state"] == query_params["state"]
    ):
        try:
            flow = get_flow()
            flow.fetch_token(code=query_params["code"])
            st.session_state.credentials = creds_to_dict(flow.credentials)
            # Clear query params and rerun
            st.query_params.clear()
            st.rerun()
        except Exception as e:
            st.error(f"Authentication failed: {str(e)}")
            st.query_params.clear()
    else:
        st.error("Invalid state parameter. Please try logging in again.")
        st.query_params.clear()

creds = get_credentials()

if creds:
    st.success("✅ Authenticated with Google")
    
    if st.button("🚪 Logout"):
        # Clear all session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    youtube = get_youtube_service()
    if youtube:
        try:
            # Get user's channels
            channels = (
                youtube.channels()
                .list(part="snippet,statistics", mine=True)
                .execute()
            )
            
            if channels.get("items"):
                channel = channels["items"][0]
                st.subheader(f"📺 Channel: {channel['snippet']['title']}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Subscribers", channel["statistics"]["subscriberCount"])
                with col2:
                    st.metric("Total Videos", channel["statistics"]["videoCount"])
                with col3:
                    st.metric("Total Views", channel["statistics"]["viewCount"])
                
                # Show raw data
                with st.expander("📊 Raw Channel Data"):
                    st.json(channels)
            else:
                st.warning("No channels found for this account.")
                
        except Exception as e:
            st.error(f"Error fetching YouTube data: {str(e)}")
            st.info("Make sure your Google account has a YouTube channel.")
else:
    st.info("👋 Please authenticate with Google to access your YouTube data.")
    
    if st.button("🔐 Login with Google", type="primary"):
        flow = get_flow()
        auth_url, state = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent",
        )
        st.session_state["state"] = state
        st.markdown(f"**[🔗 Click here to authenticate with Google]({auth_url})**")
        st.info("👆 Click the link above to sign in with your Google account")
