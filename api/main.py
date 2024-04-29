from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import subprocess
import re

from api.routers import lmm
from api.routers import file
from api.routers import user

from dotenv import load_dotenv

load_dotenv()
app = FastAPI(
    title="TeamC LMM API",
)

@app.get("/")
async def hello():
    return {"message": "hello world!"}

@app.get("/gpudata")
async def read_gpudata():
    # nvidia-smiコマンドを実行
    result = subprocess.run(['nvidia-smi'], stdout=subprocess.PIPE, text=True)
    output = result.stdout
    
    # GPU使用率を抽出
    gpu_util_match = re.search(r'(\d+)%\s+Default', output)
    if gpu_util_match:
        gpu_util = gpu_util_match.group(1)
    else:
        gpu_util = "N/A"  # 使用率が見つからない場合

    return {"gpu_util": f"{gpu_util}%"}

app.include_router(lmm.router,prefix="/lmm")
app.include_router(file.router,prefix="/file")
app.include_router(user.router,prefix="/user")

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)