from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from database import SessionLocal, User, FileMetadata
import pandas as pd
import uuid

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Upload CSV File
@router.post("/upload/",tags=["File processing"])
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
