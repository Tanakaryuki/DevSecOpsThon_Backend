from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import subprocess
import re

from api.routers import lmm
from api.routers import file
from api.routers import user
from api.routers import clip

from dotenv import load_dotenv
import logging

load_dotenv()
app = FastAPI(
    title="TeamC LMM API",
)

@app.get("/")
async def hello():
    return {"message": "hello world!"}

def run_command(command: str) -> str:
    """ コマンドを実行し、標準出力を返す """
    result = subprocess.run(command, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.stdout


@app.get("/gpudata")
async def read_gpu_data():
    try:
        # ファイルからGPU使用率を読み込む
        with open("/gpudata/gpudata.txt", "r") as file:
            gpu_util = file.read().strip()
            return {"gpu_util": f"{gpu_util}"}
    except Exception as e:
            return {"gpu_util": f"{0}"}


app.include_router(lmm.router,prefix="/lmm")
app.include_router(file.router,prefix="/file")
app.include_router(user.router,prefix="/user")
app.include_router(clip.router,prefix="/clip")

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)