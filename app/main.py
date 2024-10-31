from fastapi import FastAPI, UploadFile, HTTPException
import os
from pydantic import BaseModel
from dotenv import load_dotenv
import openai
import shutil
import io

app = FastAPI()

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY


class Question(BaseModel):
    question: str


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/greet/{name}")
def read_item(name: str):
    return {"Hello": name}


@app.post("/uploadfile/")
async def upload_file(file: UploadFile):
    # Define allowed extensions
    allowed_extensions = ["txt", "pdf"]
    # Check if the file extension is allowed
    if file.filename is None:
        raise HTTPException(status_code=400, detail="Invalid filename!")
    file_extension = file.filename.split('.')[-1]
    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail="File type not allowed")
    folder = "sources"
    try:
        os.makedirs(folder, exist_ok=True)
        file_location = os.path.join(folder, file.filename)
        file_content = await file.read()
        with open(file_location, "wb+") as file_object:
            file_like_object = io.BytesIO(file_content)
            shutil.copyfileobj(file_like_object, file_object)
    except Exception as e:
        print(f"Error saving file: {e}")
        raise HTTPException(status_code=500, detail="Error saving file")
    return {"info": "File Saved", "file": file.filename}


@app.post("/ask/")
async def ask_question(question: Question):
    if OPENAI_API_KEY is None:
        raise HTTPException(status_code=500, detail="OpenAI key not set!")
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You're a good astt"},
                {"role": "user", "content": question.question},
                ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"response": response.choices[0].message.content}
