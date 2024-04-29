import subprocess
import re
import time

def run_command(command: str) -> str:
    """ コマンドを実行し、標準出力を返す """
    result = subprocess.run(command, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.stdout

def get_gpu_data():
    # 'docker top api' コマンドを実行
    docker_top_output = run_command("docker top api")
    
    # 出力からPPIDを取得
    lines = docker_top_output.splitlines()
    if len(lines) < 9:
        return {"error": "Not enough lines in docker top output"}
    
    target_line = lines[8]  # 9行目を選択（インデックスは0から始まるため8）
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

def update_gpu_data_file():
    while True:
        gpu_data = get_gpu_data()
        if "GPU Memory" in gpu_data:
            gpu_memory = gpu_data["GPU Memory"]
            with open("/home/teamC/DevSecOpsThon_Backend/gpudata/gpudata.txt", "w") as file:
                print(gpu_memory)
                file.write(gpu_memory)
        else:
            print("Error retrieving GPU data:", gpu_data.get("error", "Unknown error"))
        time.sleep(0.5)

if __name__ == "__main__":
    update_gpu_data_file()
