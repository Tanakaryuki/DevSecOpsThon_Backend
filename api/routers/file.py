from fastapi import APIRouter,HTTPException,status,File,UploadFile,BackgroundTasks
import os

router = APIRouter()

async def add_data(file_path:str):
    pass
    # ここにベクトルDBにデータを追加する処理を書く or LLMの関数を呼び出す処理を書く

@router.post("",tags=["file"])
async def post_file(background_tasks: BackgroundTasks,file: UploadFile = File(...)) -> dict:
    contents = await file.read()
    save_directory = "/home/teamC/files/"

    file_path = os.path.join(save_directory, file.filename)

    with open(file_path, "wb") as f:
        f.write(contents)
    
    # background_tasks.add_task(add_data, file_path)
    # add_data関数が完成したらコメントアウトを外す

    raise HTTPException(status_code=status.HTTP_202_ACCEPTED, detail="File uploaded successfully")