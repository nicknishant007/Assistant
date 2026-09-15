from pydantic import BaseModel, ConfigDict


class UserProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    full_name: str | None = None
    profile_picture: str | None = None


class UserProfileUpdateRequest(BaseModel):
    full_name: str | None = None
    profile_picture: str | None = None