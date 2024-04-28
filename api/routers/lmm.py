from fastapi import FastAPI, APIRouter,Depends,HTTPException,status
from fastapi.responses import StreamingResponse
import asyncio
import random
from llm.chat import qa_system

router = APIRouter()

@router.get("/streaming",tags=["lmm"])
async def get_streaming(question: str) -> StreamingResponse:
    message, sources = qa_system(question)
    
    result = f"""__捨てる場所__  
    {message}
    __ソース__  
    {sources}
    """
    
    async def generate():
        for char in result:
            await asyncio.sleep(random.randint(1,100) * 0.001)
            yield f"{char}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")

@router.get("/question",tags=["lmm"])
async def get_question(question: str) -> dict:
    message, sources = qa_system(question)
    return {"message": message, "sources": sources}
