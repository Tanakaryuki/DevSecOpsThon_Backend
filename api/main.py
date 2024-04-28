from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import lmm

from dotenv import load_dotenv


load_dotenv()
app = FastAPI()

@app.get("/hello")
async def hello():
    return {"message": "hello world!"}

app.include_router(lmm.router,prefix="/lmm")

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)