from pydantic import BaseModel


class CreateEventRequest(BaseModel):

    title: str
    start_time: str
    end_time: str



class UpdateEventRequest(BaseModel):

    event_id: str
    title: str |None = None
    start_time: str
    end_time: str


class DeleteEventRequest(BaseModel):

    event_id: str


class FindEventRequest(BaseModel):
    title: str
    date: str | None = None
    day: str | None = None