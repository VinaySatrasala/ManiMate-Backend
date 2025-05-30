from fastapi import APIRouter, HTTPException
from app.core.app import App
router = APIRouter()


@router.post("/generate")
def generate_video(prompt: str):
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    
    app = App()
    app.set_prompt(prompt)
    return {
        "message": "Video generation started",
        "prompt": prompt,
        "response": app.generate_script()
    }
