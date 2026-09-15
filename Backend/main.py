from config.settings import settings
from fastapi import FastAPI,Request
from fastapi.responses import JSONResponse
import traceback
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from api.routes.auth import router as auth_router
from api.routes.scheduler import router as scheduler_router
from api.routes.chat import router as chat_router
from api.routes.voice import router as voice_router
from api.routes.conversations import router as conversations_router

app = FastAPI(
    title="AI Executive Assistant",
    version="1.0.0"
) 
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SESSION_SECRET_KEY
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(scheduler_router)
app.include_router(voice_router)
app.include_router(conversations_router)
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