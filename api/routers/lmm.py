from fastapi import FastAPI, APIRouter,Depends,HTTPException,status
from fastapi.responses import StreamingResponse
import asyncio

from llm.chat import qa_system

router = APIRouter()

@router.get("/streaming",tags=["lmm"])
async def get_streaming(question: str) -> StreamingResponse:
    message, sources = qa_system(question)
    async def generate():
        for char in message:
            await asyncio.sleep(0.05)
            yield f"data: {char}\n\n"
        for char in sources:
            await asyncio.sleep(0.01)
            yield f"data: {char}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")

@router.get("/question",tags=["lmm"])
async def get_question(question: str) -> dict:
    message, sources = qa_system(question)
    return {"message": message, "sources": sources}
