from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import FileResponse
from typing import Optional, List
from pathlib import Path

from app.core.app import App
from app.models.schema import PromptSchema, VideoSchema, ChatResponse

router = APIRouter()

@router.post("/generate", response_model=ChatResponse)
def generate_video(request: PromptSchema):
    prompt = request.prompt
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    
    app = App()
    app.set_prompt(prompt, request.chat_id)
    response = app.generate_script()
    return ChatResponse(
        chat_id=response["chat_id"],
        response=response["script_cleaned"],
        messages=response["messages"]
    )

@router.post("/getvideo")
async def get_video(req: VideoSchema = Body(...)):
    filename = req.filename
    video_path = Path(f"static/videos/{filename}.mp4")

    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Video not found")

    return {
        "video_url": f"/videos/{filename}.mp4"
    }

@router.get("/chats")
async def list_chats():
    app = App()
    return app.chat_manager.list_chats()