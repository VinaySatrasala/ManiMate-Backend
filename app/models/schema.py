from pydantic import BaseModel

class PromptSchema(BaseModel):
    prompt : str

