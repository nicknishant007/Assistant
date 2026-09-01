from services.calendar_service import (get_events,find_event_by_title)


def get_events_tool(
    db,
    user_id: str,
    max_results: int = 20
):
    return get_events(
        db=db,
        user_id=user_id,
        max_results=max_results
    )


def find_event_by_title_tool(
    db,
    user_id: str,
    title: str
):
    return find_event_by_title(
        db=db,
        user_id=user_id,
        title=title
    )