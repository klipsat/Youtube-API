import streamlit as st
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
]


def get_flow():
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


st.set_page_config(page_title="YouTube Insights Tool")

st.title("YouTube Insights Tool")

# Handle OAuth2 redirect
query_params = st.experimental_get_query_params()

if "credentials" not in st.session_state:
    if "code" in query_params and "state" in query_params:
        if (
            "state" in st.session_state
            and st.session_state["state"] == query_params["state"][0]
        ):
            flow = get_flow()
            flow.fetch_token(code=query_params["code"][0])
            st.session_state.credentials = creds_to_dict(flow.credentials)
            st.experimental_set_query_params()  # clear params
            st.success("Successfully authenticated!")
            st.experimental_rerun()
    else:
        if st.button("Login with Google"):
            flow = get_flow()
            auth_url, state = flow.authorization_url(
                access_type="offline",
                include_granted_scopes="true",
                prompt="consent",
            )
            st.session_state["state"] = state
            st.write("Please continue the login in a new tab:")
            st.markdown(f"[Authorize]({auth_url})")
else:
    creds = Credentials(**st.session_state.credentials)
    youtube = build("youtube", "v3", credentials=creds)
    st.write("Authenticated! You can now access the API.")
    # Example: list the user's channels
    channels = (
        youtube.channels()
        .list(part="snippet,statistics", mine=True)
        .execute()
    )
    st.json(channels)
