from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Digital Wardrobe Ingestion API")

@app.get("/")
def read_root():
    return {"status": "healthy", "service": "wardrobe-ingestion"}

from services.s3 import s3_service
from services.pinecone import pinecone_service
from services.mongo import mongo_service
from worker import worker
import uuid
import os
import shutil

@app.post("/ingest")
async def ingest_item(file: UploadFile = File(...)):
    # 1. Save temp file for processing
    temp_filename = f"temp_{uuid.uuid4()}_{file.filename}"
    with open(temp_filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # 2. Upload to S3
        # Reset file pointer for S3 upload or re-open temp file
        with open(temp_filename, "rb") as f:
            s3_url = s3_service.upload_file(f, f"raw/{file.filename}")
        
        if not s3_url:
            # Fallback for local dev/mock
            s3_url = f"https://mock-s3.com/{file.filename}"

        # 3. Generate Embedding
        vector = worker.process_image(temp_filename)
        
        # 4. Index in Pinecone
        vector_id = str(uuid.uuid4())
        metadata = {
            "filename": file.filename,
            "s3_url": s3_url,
            "content_type": file.content_type
        }
        pinecone_service.upsert_vector(vector_id, vector, metadata)
        
        # 5. Store Metadata in MongoDB
        item_record = {
            "_id": vector_id,
            "filename": file.filename,
            "s3_url": s3_url,
            "vector_id": vector_id,
            "content_type": file.content_type,
            "status": "processed"
        }
        mongo_service.insert_item(item_record)
        
        return {
            "status": "success",
            "item_id": vector_id,
            "s3_url": s3_url,
            "vector_preview": vector[:5] # Show first 5 dims
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        # Cleanup temp file
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
