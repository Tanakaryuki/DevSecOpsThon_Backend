from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import lmm
from api.routers import file

from dotenv import load_dotenv

load_dotenv()
app = FastAPI(
    title="TeamC LMM API",
)

@app.get("/")
async def hello():
    return {"message": "hello world!"}

app.include_router(lmm.router,prefix="/lmm")
app.include_router(file.router,prefix="/file")

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)