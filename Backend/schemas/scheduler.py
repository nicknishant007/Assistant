from pydantic import BaseModel
from datetime import datetime


class ScheduleTaskRequest(BaseModel):

    title: str

    duration_minutes: int

    date: datetime