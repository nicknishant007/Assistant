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
from Backend.database.models.user import User
from fastapi.responses import JSONResponse

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

    token = await oauth.google.authorize_access_token(
        request
    )

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

    access_token = create_access_token(
        {
            "sub": user.id,
            "email": user.email
        }
    )

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