from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import subprocess
import re

from api.routers import lmm
from api.routers import file
from api.routers import user
# from api.routers import clip

from dotenv import load_dotenv

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
async def get_gpu_data():
    # 'docker top api' コマンドを実行
    docker_top_output = run_command("docker top api")
    
    # 出力からPPIDを取得
    lines = docker_top_output.splitlines()
    target_line = lines[7]  # 8行目を選択
    ppid = target_line.split()[2]  # PPIDの位置
    
    # 'nvidia-smi' コマンドを実行
    nvidia_smi_output = run_command("nvidia-smi")
    
    # PPIDを含む行からGPUメモリ使用量を抽出
    gpu_memory_regex = re.compile(r'\b' + re.escape(ppid) + r'\b.*?(\d+)MiB')
    match = gpu_memory_regex.search(nvidia_smi_output)
    
    if match:
        gpu_memory = match.group(1)
        return {"PPID": ppid, "GPU Memory": gpu_memory}
    else:
        return {"error": "PPID not found in GPU data"}

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
# app.include_router(clip.router,prefix="/clip")

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)