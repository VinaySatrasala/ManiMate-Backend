from fastapi import APIRouter, HTTPException
from core.llm_config import LangchainLLMConfig

router = APIRouter()
config = LangchainLLMConfig()
llm = config.langchain_llm  # ✅ Don't call it as a method

@router.post("/generate")
def generate_video(prompt: str):
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    
    response = llm.invoke(prompt)  # You can also wrap this in try/except for safety
    return {
        "message": "Video generation started",
        "prompt": prompt,
        "response": response
    }
