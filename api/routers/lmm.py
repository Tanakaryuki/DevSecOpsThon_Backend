from fastapi import FastAPI, APIRouter,Depends,HTTPException,status
from fastapi.responses import StreamingResponse
import asyncio

from llm.chat import qa_system

router = APIRouter()

@router.get("/streaming",tags=["lmm"])
async def get_streaming() -> StreamingResponse:
    async def generate():
        for i in range(10):
            yield f"data: {i}\n\n"
            await asyncio.sleep(0.5)

    return StreamingResponse(generate(), media_type="text/event-stream")

@router.get("/question",tags=["lmm"])
async def get_question() -> dict:
    text = "ここに質問が来る"
    message, sources = qa_system(text)
    return {"message": message, "sources": sources}
