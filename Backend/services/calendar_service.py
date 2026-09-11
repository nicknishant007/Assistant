from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from config.settings import settings

from services.integration_service import (get_google_integration)
from datetime import datetime,timezone,timedelta
from utils.date_resolver import resolve_day_name,resolve_day_of_month

def build_calendar_service(
    db,
    user_id: str
):

    integration = get_google_integration(
        db=db,
        user_id=user_id
    )

    if not integration:
        raise Exception(
            "Google Calendar not connected"
        )

    credentials = Credentials(
        token=integration.access_token,
        refresh_token=integration.refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET
    )

    # Refresh expired token
    if credentials.expired and credentials.refresh_token:

        credentials.refresh(Request())

        integration.access_token = credentials.token

        db.commit()
        db.refresh(integration)

    service = build(
        "calendar",
        "v3",
        credentials=credentials
    )

    return service

def get_events(
        db,
        user_id:str,
        max_results:int=100):
    service=build_calendar_service(
        db=db,
        user_id=user_id
)
    events=(
        service.events().list(
            calendarId="primary",
            timeMin=datetime.now(
                timezone.utc).isoformat(),
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime"
            ).execute()
        )
    return events.get("items",[])

##creat event  
def create_event(
    db,
    user_id: str,
    title: str,
    start_time: str,
    end_time: str
):
    
    service = build_calendar_service(
        db=db,
        user_id=user_id
    )
    if isinstance(start_time, datetime):
        start_time = start_time.isoformat()

    if isinstance(end_time, datetime):
        end_time = end_time.isoformat()
    event = {
        "summary": title,
        "start": {
            "dateTime": start_time,
            "timeZone": "Asia/Kolkata"
        },
        "end": {
            "dateTime": end_time,
            "timeZone": "Asia/Kolkata"
        }
    }

    created_event = (
        service.events()
        .insert(
            calendarId="primary",
            body=event
        )
        .execute()
    )

    return {
        "success":True,
        "event":created_event
    }

##UPDATE EVENT
def update_event(
    db,
    user_id: str,
    event_id: str,
    title: str,
    start_time: str,
    end_time: str
):

    service = build_calendar_service(
        db=db,
        user_id=user_id
    )
    if isinstance(start_time, datetime):
        start_time = start_time.isoformat()

    if isinstance(end_time, datetime):
        end_time = end_time.isoformat()

    event = {
        "summary": title,
        "start": {
            "dateTime": start_time,
            "timeZone": "Asia/Kolkata"
        },
        "end": {
            "dateTime": end_time,
            "timeZone": "Asia/Kolkata"
        }
    }

    updated_event=(
        service.events()
        .update(
            calendarId="primary",
            eventId=event_id,
            body=event
        )
        .execute()
    )
    print("UPDATE EVENT CALLED")
    print("event_id =", event_id)
    print("start_time =", start_time)
    print("end_time =", end_time)
    return{
        "success":True,
        "event":updated_event
    }

#Delete Event
def delete_event(
    db,
    user_id: str,
    event_id: str
):

    service = build_calendar_service(
        db=db,
        user_id=user_id
    )

    service.events().delete(
        calendarId="primary",
        eventId=event_id
    ).execute()

    return {
        "success":True,
        "event_id":event_id,
        "message": "Event Deleted"
    }


#get that day events
def get_day_events(
    service,
    date: datetime
):

    start_of_day = datetime(
        date.year,
        date.month,
        date.day,0,0,0,tzinfo=timezone.utc
    )

    end_of_day = start_of_day + timedelta(days=1)

    events = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=start_of_day.isoformat(),
            timeMax=end_of_day.isoformat(),
            singleEvents=True,
            orderBy="startTime"
        )
        .execute()
    )

    return events.get("items", [])

##GET 7 DAY EVENT

def get_events_range(
    service,
    start_date: datetime,
    end_date: datetime
):

    if start_date.tzinfo is None:
        start_date = start_date.replace(
            tzinfo=timezone.utc
        )

    if end_date.tzinfo is None:
        end_date = end_date.replace(
            tzinfo=timezone.utc
        )

    events = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=start_date.isoformat(),
            timeMax=end_date.isoformat(),
            singleEvents=True,
            orderBy="startTime"
        )
        .execute()
    )

    return events.get("items", [])



# FIND EVENT BY TITLE


def find_event_by_title(
    db,
    user_id: str,
    title: str,
    date: str | None = None,
    day: str | None = None
):

    if not title.strip():
        return {
            "found": False,
            "message": "Title is required.",
            "best_match": None,
            "alternatives": []
        }

    resolved_date = None
    resolved_day = None

    if date:
        resolved_date = resolve_day_of_month(
            int(date)
        )

    if day:
        resolved_day = (
            day.lower()
            .strip()
        )

    events = get_events(
        db=db,
        user_id=user_id,
        max_results=100
    )

    query = (
        title.lower()
        .strip()
    )

    scored_events = []

    for event in events:

        event_title = (
            event.get("summary", "")
            .lower()
            .strip()
        )

        title_score = 0
        date_score = 0
        day_score = 0

        # -------------------
        # TITLE SCORE
        # -------------------

        if event_title == query:

            title_score = 100

        elif query in event_title:

            title_score = 80

        else:

            query_words = set(
                query.split()
            )

            title_words = set(
                event_title.split()
            )

            overlap = len(
                query_words.intersection(
                    title_words
                )
            )

            title_score = overlap * 20

        # -------------------
        # EVENT DATA
        # -------------------

        try:

            start_info = event.get(
                "start",
                {}
            )

            end_info = event.get(
                "end",
                {}
            )

            start_datetime = (
                start_info.get("dateTime")
                or start_info.get("date")
            )

            end_datetime = (
                end_info.get("dateTime")
                or end_info.get("date")
            )

            duration_minutes = None
            start_time = None
            end_time = None
            event_date = None
            event_day = None

            if start_datetime:

                start_dt = datetime.fromisoformat(
                    start_datetime.replace(
                        "Z",
                        "+00:00"
                    )
                )

                start_time = (
                    start_dt.strftime("%H:%M")
                )

                event_date = (
                    start_dt.date()
                    .isoformat()
                )

                event_day = (
                    start_dt.strftime("%A")
                    .lower()
                )

                if (
                    resolved_date
                    and event_date == resolved_date
                ):
                    date_score = 100

                if (
                    resolved_day
                    and event_day == resolved_day
                ):
                    day_score = 100

                if end_datetime:

                    end_dt = datetime.fromisoformat(
                        end_datetime.replace(
                            "Z",
                            "+00:00"
                        )
                    )

                    end_time = (
                        end_dt.strftime("%H:%M")
                    )

                    duration_minutes = int(
                        (
                            end_dt - start_dt
                        ).total_seconds() / 60
                    )

        except Exception:
            continue

        # -------------------
        # FINAL SCORE
        # -------------------

        score = title_score

        if resolved_date:
            score += date_score * 0.3

        if resolved_day:
            score += day_score * 0.2

        if score > 0:

            scored_events.append({
                "event_id": event.get("id"),
                "title": event.get("summary"),

                "start_datetime": start_datetime,
                "end_datetime": end_datetime,

                "start_time": start_time,
                "end_time": end_time,

                "date": event_date,
                "day": event_day,

                "duration_minutes": duration_minutes,

                "score": round(score, 2)
            })

    if not scored_events:

        return {
            "found": False,
            "message": "No events found matching the title.",
            "best_match": None,
            "alternatives": []
        }

    scored_events.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    top_events = scored_events[:3]

    return {
        "found": True,
        "best_match": top_events[0],
        "alternatives": top_events[1:]
    }