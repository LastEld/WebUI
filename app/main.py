#main.py


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

# --- Для prod конфіг, логування, env ---
import logging
import os

# --- Auto Import All Routers ---
from app.api import (
    ai_context, auth, devlog, jarvis, plugin, project, settings,
    task, team, template, token_refresh, user
)
from app.core.settings import settings
print(settings.DATABASE_URL)
print(settings.SECRET_KEY)


# --- Для docs ---
API_TITLE = "DevOS Jarvis Web API"
API_VERSION = "1.0.0"

# --- CORS (можно расширять по нуждам) ---
origins = [
    "http://localhost:3000",   # Frontend local
    "http://127.0.0.1:3000",
    "https://your-production-frontend.com",
]

app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description="Backend for modular AI-ready project manager (FastAPI)",
)

# --- CORS middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Session middleware (якщо треба куки для auth) ---
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY", "CHANGEME-SECRET"),
)

# --- Routers ---
app.include_router(ai_context.router)
app.include_router(auth.router)
app.include_router(devlog.router)
app.include_router(jarvis.router)
app.include_router(plugin.router)
app.include_router(project.router)
app.include_router(settings.router)
app.include_router(task.router)
app.include_router(team.router)
app.include_router(template.router)
app.include_router(token_refresh.router)
app.include_router(user.router)

# --- Healthcheck and Root ---
@app.get("/", tags=["Health"])
def read_root():
    return {"status": "DevOS Jarvis Web API is running!"}

@app.get("/health", tags=["Health"])
def health():
    return {"ok": True}

# --- Custom Exception handlers, error schemas, logging can be added here ---
# Example: from app.schemas.response import ErrorResponse

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", reload=True)
