from datetime import time
from pydantic import BaseModel, ConfigDict


class PreferencesResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    wake_time: time | None = None
    sleep_time: time | None = None
    work_start_time: time | None = None
    focus_duration: int


class PreferencesUpdateRequest(BaseModel):
    wake_time: time | None = None
    sleep_time: time | None = None
    work_start_time: time | None = None
    focus_duration: int | None = None