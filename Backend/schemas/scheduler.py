from pydantic import BaseModel
from datetime import (datetime, date, time)
from typing import Optional


class ScheduleTaskRequest(BaseModel):
    title: str
    start_datetime: datetime
    duration_minutes: int


class RescheduleTaskRequest(BaseModel):

    event_id: str
    title: str

    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None

    date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None