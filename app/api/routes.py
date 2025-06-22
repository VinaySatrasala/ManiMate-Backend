
from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path
 
from app.core.app_instance import app_instance
from app.core.app_context import app_context
from app.models.schema import PromptSchema
from app.utils.auth import *
from app.utils.exceptions import SessionLimitReachedException
app = app_instance

router = APIRouter()


class VideoSchema(BaseModel):
    filename: str


class SessionSchema(BaseModel):
    session_name: str


class SessionIdSchema(BaseModel):
    session_id: str


@router.post("/create-session")
def create_session(
    request: SessionSchema,
    user: User = Depends(get_current_user)
):
    session_name = request.session_name
    if not session_name:
        raise HTTPException(
            status_code=400, detail="Session name cannot be empty")
    try:
        session_data = app_context.db_manager.create_session(session_name, user.id)
        return {"success": True, "session": session_data}
    
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))

    except SessionLimitReachedException as sle:
        raise HTTPException(status_code=400, detail=str(sle))

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error.")

@router.get("/sessions")
def get_sessions(
    user: User = Depends(get_current_user)
):
    """
    Fetch all sessions for the current user.
    """
    sessions = app_context.db_manager.get_user_sessions(user_id=user.id)
    if not sessions:
        raise HTTPException(status_code=404, detail="No sessions found")

    return {
        "message": "Sessions retrieved successfully",
        "sessions": [session for session in sessions]
    }


@router.post("/generate")
def generate_video(
    request: PromptSchema,
    user: User = Depends(get_current_user)
):
    prompt = request.prompt
    session_id = request.session_id
    if not session_id:
        raise HTTPException(
            status_code=400, detail="Session ID cannot be empty")
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    app.set_prompt(prompt)

    response = app.generate_script(session_id, user.id)
    return {
        "message": "Video generation started",
        "prompt": prompt,
        "response": response["script_cleaned"],
        "filename": response["filename"]
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


@router.post("/delete-session")
def delete_session(
    request: SessionIdSchema,
    user: User = Depends(get_current_user)
):
    session_id = request.session_id
    if not session_id:
        raise HTTPException(
            status_code=400, detail="Session ID cannot be empty")

    app_context.db_manager.delete_session(
        session_id=session_id, user_id=user.id)
    return {
        "message": "Session deleted successfully"
    }
