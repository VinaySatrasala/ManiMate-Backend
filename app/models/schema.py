from pydantic import BaseModel

class PromptSchema(BaseModel):
    prompt : str

class VideoSchema(BaseModel):
    filename : str

