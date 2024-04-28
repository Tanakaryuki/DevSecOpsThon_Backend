from fastapi import FastAPI, APIRouter,Depends,HTTPException,status
from fastapi.responses import StreamingResponse
import asyncio

router = APIRouter()

@router.get("/streaming",tags=["lmm"])
async def get_streaming():
    async def generate():
        for i in range(10):
            yield f"data: {i}\n\n"
            await asyncio.sleep(0.5)

    return StreamingResponse(generate(), media_type="text/event-stream")

@router.get("/hello",tags=["lmm"])
async def hello():
    return {"message": "hello world!"}