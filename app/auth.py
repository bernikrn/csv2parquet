from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from database import SessionLocal, User

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Register User
@router.post("/register/", tags=["Authentication"])
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
@router.get("/get_user_id/", tags=["Authentication"])
def get_user_id(username: str, db: Session = Depends(get_db)):
    """
    Gets user_id

    - **username**: The username
    - **Returns**: The user_id if it exists, or an error if not.
    """
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"user_id": user.id}


# Get user id
@router.post("/log_in/", tags=["Authentication"])
def get_user_id(credentials: dict, db: Session = Depends(get_db)):
    """
    Log in

    - **username**: The username
    - **password**: The username
    - **Returns**: The user_id if it exists, or an error if not.
    """
    username = credentials["username"]
    password = credentials["password"]
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not pwd_context.verify(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    return {"user_id": user.id, "mesaage": "User logged in correctly"}
