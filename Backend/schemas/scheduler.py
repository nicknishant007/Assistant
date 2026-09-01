from pydantic import BaseModel
from datetime import datetime


class ScheduleTaskRequest(BaseModel):
    title: str
    date: datetime
    duration_minutes: int


class RescheduleTaskRequest(BaseModel):
    event_name: str
    start_date: datetime
    duration_minutes: int