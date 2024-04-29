import io
import requests
import shutil
from PIL import Image
import torch
import torchvision.transforms as transforms
import japanese_clip as ja_clip
import csv
from fastapi import FastAPI, File, UploadFile,APIRouter
from fastapi.responses import StreamingResponse
from starlette.responses import JSONResponse
import asyncio
import random
from llm.chat import qa_system

router = APIRouter()

def predict_image_label(image, model, preprocess, tokenizer, labels):
    img = image.resize((256, 256))
    image = preprocess(img).unsqueeze(0).to(device)
    encodings = ja_clip.tokenize(
        texts=labels,
        max_seq_len=77,
        device=device,
        tokenizer=tokenizer
    )
    with torch.no_grad():
        image_features = model.get_image_features(image)
        text_features = model.get_text_features(**encodings)
        text_probs = (100.0 * image_features @ text_features.T).softmax(dim=-1)
    predicted_label_index = text_probs.argmax().item()
    predicted_label = labels[predicted_label_index]
    return predicted_label, text_probs

device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = ja_clip.load("rinna/japanese-clip-vit-b-16", cache_dir="/tmp/japanese_clip", device=device)
tokenizer = ja_clip.load_tokenizer()
labels = []
with open("csv/output.csv", "r", newline="", encoding="utf-8") as csvfile:
    reader = csv.reader(csvfile)
    next(reader)
    for row in reader:
        labels.append(row[0])

@router.post("/predict/")
async def predict(upload_file: UploadFile = File(...)):
    try:
        contents = await upload_file.read()
        img = Image.open(io.BytesIO(contents))
        
        # Perform prediction using your existing function
        predicted_label, _ = predict_image_label(
            img, model, preprocess, tokenizer, labels
        )
        
        # Return the predicted label
        message, sources = qa_system(predicted_label)
    
        result = f"""__捨てる場所__  
        {message}
        __ソース__  
        {sources}
        """
        
        async def generate():
            for char in result:
                await asyncio.sleep(random.randint(1,100) * 0.001)
                yield f"{char}\n\n"

        return StreamingResponse(generate(), media_type="text/event-stream")
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
