# main.py
from fastapi import FastAPI, UploadFile, File, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from typing import List
import os
import json
import shutil
from markdown import markdown

import uuid
import file2vectorfaiss
from openai import OpenAI
API_KEY = 'sk-405c6b0841a84472b9d0ed8eb57072d5'
app = FastAPI()

# 设置静态文件和模板目录
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# 上传文件保存目录
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/chat")
async def chat(message: str = Form(...)):
    """
    处理用户聊天消息
    """
 
    answer = file2vectorfaiss.qa_system(message)

    html_message = markdown(answer.replace("\n", ""))
    response = html_message
    return JSONResponse(content=response)

@app.post("/api/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    """
    处理文件上传
    """
    saved_files = []
    
    for file in files:
        # 生成唯一文件名
        file_ext = os.path.splitext(file.filename)[1]
        new_filename = f"{uuid.uuid4().hex}{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, new_filename)
        
        # 保存文件
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        saved_files.append({
            "original_name": file.filename,
            "saved_name": new_filename,
            "size": os.path.getsize(file_path)
        })
    
    return {f'文件上传成功!成功上传 {len(saved_files)} 个文件'}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)