# app/routers/auth_router.py
from fastapi import APIRouter, Depends, Response, HTTPException
from pydantic import BaseModel
from uuid import uuid4
from app.models.schema import SignInModel, SignUpModel
from sqlalchemy.orm import Session
from app.models.db_models import User
from app.utils.auth import hash_password, verify_password, create_access_token
from app.core.app_context import app_context 
from app.core.app_instance import app_instance
router = APIRouter()
app = app_instance


@router.post("/signup")
def signup(user: SignUpModel):
    if app_context.db_manager.user_exists(user.user_name):
        raise HTTPException(status_code=409, detail="Username already exists")
    user.password = hash_password(user.password)                            
    new_user = app_context.db_manager.create_user(user)
    return {"message": "User registered successfully", "user_id": new_user["id"]}

@router.post("/signin")
def signin(user: SignInModel, response: Response):
    if not app_context.db_manager.user_exists(user.user_name):
        raise HTTPException(status_code=409, detail="Username not exists")
    
    if not verify_password(user.password, app_context.db_manager.get_password_hash(user.user_name)):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"sub": user.user_name, "id": user.user_name})
    response.set_cookie(
        key="access_token", value=token, httponly=True,
        samesite="Lax", secure=False  # Use `secure=True` in prod
    )
    return {"message": "Login successful"}

@router.post("/signout")
def signout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logged out"}
