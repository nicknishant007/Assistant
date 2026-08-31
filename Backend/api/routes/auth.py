from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from starlette.requests import Request
from database.session import get_db
from services.google_oauth import oauth
from config.settings import settings
from utils.security import create_access_token
from services.user_service import (get_user_by_email,create_user)
from dependencies.auth import get_current_user
from database.models.user import User
from fastapi.responses import JSONResponse
from services.integration_service import create_or_update_integration
from services.integration_service import get_google_integration
from services.calendar_service import build_calendar_service
from services.calendar_service import (get_events,create_event,delete_event,update_event)
from schemas.calendar import CreateEventRequest
from schemas.calendar import UpdateEventRequest
from schemas.calendar import DeleteEventRequest
from services.calendar_service import get_calendar_service



router = APIRouter(
    prefix="/api/auth",
    tags=["auth"]
)


@router.get("/login/google")
async def login_google(
    request: Request
):

    return await oauth.google.authorize_redirect(
        request,
        settings.GOOGLE_REDIRECT_URI
    )


@router.get("/callback/google")
async def callback_google(
    request: Request,
    db: Session = Depends(get_db)
):
    #google token
    token = await oauth.google.authorize_access_token(
        request
    )
    print("Google Token:", token)
    #access and refresh tokens from google
    google_access_token=token.get("access_token")
    google_refresh_token=token.get("refresh_token")


    user_info = token.get("userinfo")

    email = user_info["email"]
    name = user_info["name"]
    picture = user_info.get("picture")

    user = get_user_by_email(
        db,
        email
    )

    if not user:

        user = create_user(
            db=db,
            email=email,
            full_name=name,
            profile_picture=picture
        )
    #save google token in db
    create_or_update_integration(
        db=db,
        user_id=user.id,
        provider="google_calendar",
        access_token=google_access_token,
        refresh_token=google_refresh_token
    )
    #create jwt
    access_token = create_access_token(
        {
            "sub": user.id,
            "email": user.email
        }
    )
    print("JWT Access Token:", access_token)
    #set cookies 
    response = JSONResponse(
        {
            "message": "Login Successful",
            "user_id": user.id,
            "email": user.email
        }
    )

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,      # True in production
        samesite="lax",
        max_age=60 * 60 * 24 * 7
    )

    return response

#GET CURRENT USER
@router.get("/me")
async def get_me(
    current_user: User=Depends(get_current_user)):#before running this endpoint, make sure to login with google and get the access token in the cookie 
                                                   #(Depends(get_current_user) will extract the user from the access token in the cookie)
    return{
        "id":current_user.id,
        "email":current_user.email,
        "name":current_user.full_name
    }

#LOGOUT
@router.post("/logout")
async def logout():
    response=JSONResponse(
            {"message":"Logout Successful"}
        )
    response.delete_cookie(
            key="access_token"
        )
    return response



@router.get("/test-integration")
async def test_integration(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    
    integration = get_google_integration(
        db,
        current_user.id
    )

    return {
        "provider": integration.provider,
        "connected": integration.connected
    }

#Build Google Calendar Service
@router.get("/calendar/test")
async def calendar_test(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    service = build_calendar_service(
        db=db,
        user_id=current_user.id
    )

    calendars = (
        service.calendarList()
        .list()
        .execute()
    )

    return calendars

#Calender Events
@router.get("/events")
async def get_calendar_events(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    
    events = get_events(
        db=db,
        user_id=current_user.id
    )

    return {
        "count": len(events),
        "events": events
    }
#creat event
@router.post("/events")
async def create_calendar_event(
    payload: CreateEventRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    
    event = create_event(
        db=db,
        user_id=current_user.id,
        title=payload.title,
        start_time=payload.start_time,
        end_time=payload.end_time
    )

    return event
#Update event
@router.put("/events")
async def update_calendar_event(
    data: UpdateEventRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    integration = get_google_integration(
        db,
        current_user.id
    )

    service = get_calendar_service(
        integration.access_token
    )

    event = update_event(
        service=service,
        event_id=data.event_id,
        title=data.title,
        start_time=data.start_time,
        end_time=data.end_time
    )

    return event


#Delete event
@router.delete("/events")
async def delete_calendar_event(
    data: DeleteEventRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    integration = get_google_integration(
        db,
        current_user.id
    )

    service = get_calendar_service(
        integration.access_token
    )

    return delete_event(
        service,
        data.event_id
    )