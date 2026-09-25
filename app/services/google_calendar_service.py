import datetime
import os
from zoneinfo import ZoneInfo

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from app.config import settings

SCOPES = ["https://www.googleapis.com/auth/calendar"]
TIMEZONE = ZoneInfo("Asia/Karachi")


def get_calendar_service():
    creds = None

    if os.path.exists(settings.google_token_path):
        creds = Credentials.from_authorized_user_file(settings.google_token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(settings.google_credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(settings.google_token_path, "w", encoding="utf-8") as f:
            f.write(creds.to_json())

    return build("calendar", "v3", credentials=creds)


def get_events(date: str) -> list[dict]:
    service = get_calendar_service()
    day = datetime.date.fromisoformat(date)

    start_of_day = datetime.datetime.combine(day, datetime.time.min, tzinfo=TIMEZONE)
    end_of_day = datetime.datetime.combine(day, datetime.time.max, tzinfo=TIMEZONE)

    result = service.events().list(
        calendarId="primary",
        timeMin=start_of_day.isoformat(),
        timeMax=end_of_day.isoformat(),
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    return [
        {
            "id": e["id"],
            "title": e.get("summary", "(no title)"),
            "start": e["start"].get("dateTime", e["start"].get("date")),
            "end": e["end"].get("dateTime", e["end"].get("date")),
        }
        for e in result.get("items", [])
    ]


def create_event(title: str, start_time: str, end_time: str) -> dict:
    service = get_calendar_service()

    start_dt = datetime.datetime.fromisoformat(start_time).replace(tzinfo=TIMEZONE)
    end_dt = datetime.datetime.fromisoformat(end_time).replace(tzinfo=TIMEZONE)

    conflicts = service.events().list(
        calendarId="primary",
        timeMin=start_dt.isoformat(),
        timeMax=end_dt.isoformat(),
        singleEvents=True,
    ).execute().get("items", [])

    if conflicts:
        existing = conflicts[0]
        return {
            "booked": False,
            "conflict": {
                "title": existing.get("summary", "(no title)"),
                "start": existing["start"].get("dateTime", existing["start"].get("date")),
                "end": existing["end"].get("dateTime", existing["end"].get("date")),
            },
        }

    event = {
        "summary": title,
        "start": {"dateTime": start_dt.isoformat(), "timeZone": "Asia/Karachi"},
        "end": {"dateTime": end_dt.isoformat(), "timeZone": "Asia/Karachi"},
    }
    created = service.events().insert(calendarId="primary", body=event).execute()

    return {
        "booked": True,
        "id": created["id"],
        "title": created.get("summary"),
        "start": created["start"].get("dateTime"),
        "end": created["end"].get("dateTime"),
        "link": created.get("htmlLink"),
    }