from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as api_router
from fastapi.staticfiles import StaticFiles
from app.core.app_instance import app_instance

app = FastAPI(
    title="Manim AI Backend",
    version="1.0.0",
    description= "Prompt to animation using AI and Manim"
)

app.mount("/videos", StaticFiles(directory="static/videos"), name="videos")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

@app.on_event("startup")
def initialize_app():
    app_instance.chatapp.initialize()  # Only once at startup
