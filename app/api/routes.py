
from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path

from app.core.app_instance import app_instance
from app.models.schema import PromptSchema

app = app_instance

router = APIRouter()

class VideoSchema(BaseModel):
    filename: str
@router.post("/generate")
def generate_video(request : PromptSchema):
    prompt = request.prompt
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    app.set_prompt(prompt)
    response = app.generate_script()
    return {
        "message": "Video generation started",
        "prompt": prompt,
        "response": response["script_cleaned"],
        "filename" : response["filename"]
    }

@router.post("/getvideo")
async def get_video(req: VideoSchema = Body(...)):
    filename = req.filename
    video_path = Path(f"static/videos/{filename}.mp4")

    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Video not found")

    return {
        "video_url": f"/videos/{filename}.mp4"
    }
