from fastapi import APIRouter,HTTPException,status,File,UploadFile,BackgroundTasks
from llm.chat import db
from langchain_community.document_loaders import TextLoader
import os
from glob import glob

router = APIRouter()

async def add_data(file_path: str):
    loader = TextLoader(file_path)
    documents = loader.load()
    db.add_documents(documents)

@router.post("",tags=["file"])
async def post_file(background_tasks: BackgroundTasks,file: UploadFile = File(...)) -> dict:
    contents = await file.read()
    save_directory = "/media"

    file_path = os.path.join(save_directory, file.filename)

    with open(file_path, "wb") as f:
        f.write(contents)

    background_tasks.add_task(add_data, file_path)

    raise HTTPException(status_code=status.HTTP_202_ACCEPTED, detail="File uploaded successfully")

@router.get("/file_paths", tags=["file"])
async def get_file_paths():
    file_paths = []
    csv_files = glob("llm/csv/*")
    file_paths.extend([os.path.basename(file) for file in csv_files])

    save_directory = "/media"
    saved_files = glob(f"{save_directory}/*")
    file_paths.extend([os.path.basename(file) for file in saved_files])
    
    return {"file_paths": file_paths}
