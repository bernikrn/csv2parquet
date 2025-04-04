from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, User, FileMetadata
from passlib.context import CryptContext
import pandas as pd
import os
import uuid

app = FastAPI()

# Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Register User
@app.post("/register/")
def register(username: str, password: str, db: Session = Depends(get_db)):
    hashed_password = pwd_context.hash(password)
    user = User(username=username, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "User created successfully"}

# Upload CSV File
@app.post("/upload/")
async def upload_file(file: UploadFile = File(...), username: str = "", password: str = "", db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()

    if not user or not pwd_context.verify(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    file_id = str(uuid.uuid4())
    output_filename = f"{file_id}.parquet"
    
    df = pd.read_csv(file.file)
    df.to_parquet(output_filename)

    metadata = FileMetadata(user_id=user.id, filename=file.filename, status="completed")
    db.add(metadata)
    db.commit()
    
    return {"message": "File processed successfully", "output_file": output_filename}
