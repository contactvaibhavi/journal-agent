from fastapi import FastAPI, UploadFile, HTTPException, Depends, BackgroundTasks
import os
from pydantic import BaseModel
from dotenv import load_dotenv
import openai
import shutil
import io
from app.file_parser import FileParser
from app.db import get_db, File, FileChunk
from sqlalchemy.orm import Session
from background_tasks import TextProcessor, client
from sqlalchemy import select
from pydantic import BaseModel


app = FastAPI()


class QuestionModel(BaseModel):
    question: str


class AskModel(BaseModel):
    document_id: int
    question: str

    
load_dotenv()


@app.get("/")
async def root(db: Session = Depends(get_db)):
    # Query the db for all files
    files_query = select(File)
    files = db.scalars(files_query).all()
    # Format and return the list of files including file_id and filename
    files_list = [{"file_id": file.file_id, "file_name": file.file_name} for file in files]
    return files_list


@app.get("/greet/{name}")
def read_item(name: str):
    return {"Hello": name}


@app.post("/uploadfile/")
async def upload_file(background_tasks: BackgroundTasks, file: UploadFile, db: Session = Depends(get_db)):
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
        content_parser = FileParser(file_location)
        file_text_content = content_parser.parse()
        # Save file details in the db
        new_file = File(file_name=file.filename,
                        file_content=file_text_content)
        db.add(new_file)
        db.commit()
        db.refresh(new_file)
        # Add background job for processing file content
        background_tasks.add_task(TextProcessor(db, new_file.file_id).chunk_and_embed, file_text_content)
        return {"info": "File saved", "filename": file.filename}
    except Exception as e:
        print(f"Error saving file: {e}")
        raise HTTPException(status_code=500, detail="Error saving file")
    return {"info": "File Saved", "file": file.filename}


async def get_similar_chunks(file_id: int, question: str, db: Session):
    try:
        # Create embeddings for the question
        response = client.embeddings.create(input=question, model="text-embedding-ada-002")
        question_embedding = response.data[0].embedding
        similar_chunks_query = select(FileChunk).where(FileChunk.file_id == file_id)\
            .order_by(FileChunk.embedding_vector.l2_distance(question_embedding)).limit(10)
        similar_chunks = db.scalars(similar_chunks_query).all()
        return similar_chunks
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask/")
async def ask_question(request: AskModel, db: Session = Depends(get_db)):
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    openai.api_key = OPENAI_API_KEY

    if OPENAI_API_KEY is None:
        raise HTTPException(status_code=500, detail="OpenAI key not set!")
    try:
        similar_chunks = await get_similar_chunks(request.document_id, request.question, db)

        # Construct context from the similar chunks' texts
        context_texts = [chunk.chunk_text for chunk in similar_chunks]
        context = " ".join(context_texts)
        
        # Update the system message with the context
        system_message = f"You're a helpful assistant. Here is the context to use to reply to questions: {context}"

        # Make the LLM API call with the updated context
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": request.question},
                ]
        )
        return {"response": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/find-similar-chunks/{file_id}")
async def find_similar_chunks_endpoint(file_id: int, question_data: QuestionModel, db: Session = Depends(get_db)):
    try:
        similar_chunks = await get_similar_chunks(file_id, question_data.question, db)

        # Format the response
        formatted_response = [
            {"chunk_id": chunk.chunk_id, "chunk_text": chunk.chunk_text}

            for chunk in similar_chunks
        ]

        return formatted_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
