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
@app.post("/register/", tags=["Authentication"])
def register(username: str, password: str, db: Session = Depends(get_db)):
    """
    Register a new user.

    - **username**: The desired username (must be unique).
    - **password**: The password.
    - **Returns**: A success message if registration is successful.
    """
    hashed_password = pwd_context.hash(password)
    user = User(username=username, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "User created successfully"}


# Get user id
@app.get("/get_user_id/", tags=["Authentication"])
def get_user_id(username: str, db: Session = Depends(get_db)):
    """
    Gets user_id

    - **username**: The username
    - **Returns**: The user_id if it exists, or an error if not.
    """
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user_id": user.id}


# Upload CSV File
@app.post("/upload/",tags=["File processing"])
def upload_file(file: UploadFile = File(...), username: str = "", password: str = "", db: Session = Depends(get_db)):
    """
    Process a .csv file

    - **file**: The .csv file to be processed.
    - **username**: From the user uploading the file.
    - **password**: From the user uploading the file.
    - **Returns**: A success message if file processing is successful.
    """
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
