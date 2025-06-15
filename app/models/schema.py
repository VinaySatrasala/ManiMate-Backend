from pydantic import BaseModel

class PromptSchema(BaseModel):
    prompt : str
    session_id : str

class VideoSchema(BaseModel):
    filename : str

class SignUpModel(BaseModel):
    user_name: str
    name: str
    password: str

class SignInModel(BaseModel):
    user_name: str
    password: str