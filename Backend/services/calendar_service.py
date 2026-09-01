from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from services.integration_service import (get_google_integration)
from datetime import datetime,timezone,timedelta

def build_calendar_service(
    db,
    user_id: str
):
    
    integration = get_google_integration(
        db=db,
        user_id=user_id) 

    if not integration: 
        raise Exception(
            "Google Calendar not connected"
        )

    credentials = Credentials(
        token=integration.access_token
    )

    service = build(
        "calendar",
        "v3",
        credentials=credentials
    )

    return service


def get_events(
        db,
        user_id:str,
        max_results:int=20):
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

    return created_event

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

    return (
        service.events()
        .update(
            calendarId="primary",
            eventId=event_id,
            body=event
        )
        .execute()
    )

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
        date.day,
        0,
        0,
        0,
        tzinfo=timezone.utc
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

#find event by title 
def find_event_by_title(
    db,
    user_id: str,
    title: str
):

    events = get_events(
        db=db,
        user_id=user_id,
        max_results=100
    )

    matching_events = []

    for event in events:

        if (
            event.get("summary", "")
            .lower()
            == title.lower()
        ):
            matching_events.append(
                event
            )

    return matching_events

