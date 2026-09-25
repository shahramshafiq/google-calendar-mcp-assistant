"""
CORE LOGIC, TODO: real Google Calendar integration.

Setup you'll need to do yourself first (not code, one-time setup):
1. Create a project in Google Cloud Console, enable the "Google Calendar API".
2. Create OAuth 2.0 credentials (Desktop app type), download as credentials.json,
   place it at credentials/credentials.json (path comes from settings.google_credentials_path).
3. First real run will open a browser for you to log in and grant calendar access,
   the google-auth-oauthlib flow saves a reusable token to settings.google_token_path
   automatically, you don't need to build that saving logic yourself, the library does it.

Typical library calls you'll use here (already in requirements.txt):
- google.oauth2.credentials.Credentials
- google_auth_oauthlib.flow.InstalledAppFlow
- googleapiclient.discovery.build("calendar", "v3", credentials=...)

Functions the MCP tools in server.py will need from this module:
"""

from app.config import settings


def get_events(date: str) -> list[dict]:
    """Return the calendar events on the given date (YYYY-MM-DD) from the user's primary calendar."""
    raise NotImplementedError


def create_event(title: str, start_time: str, end_time: str) -> dict:
    """Create a new calendar event (ISO 8601 start_time/end_time) and return the created event."""
    raise NotImplementedError
