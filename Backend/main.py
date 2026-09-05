from config.settings import settings
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from api.routes.auth import router as auth_router
from api.routes.scheduler import router as scheduler_router
from api.routes.chat import router as chat_router
app = FastAPI(
    title="AI Executive Assistant",
    version="1.0.0"
)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SESSION_SECRET_KEY
)

app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(scheduler_router)
@app.get("/")
async def root():
    return {
        "message": "Backend Running"
    }
app.include_router(
    scheduler_router
)

@app.get("/health")
async def health():
    return {
        "status": "healthy"
    }