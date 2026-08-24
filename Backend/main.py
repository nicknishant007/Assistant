from config.settings import settings
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from api.auth import router as auth_router

app = FastAPI(
    title="AI Executive Assistant",
    version="1.0.0"
)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SESSION_SECRET_KEY
)

app.include_router(auth_router)

@app.get("/")
async def root():
    return {
        "message": "Backend Running"
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy"
    }