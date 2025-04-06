from fastapi import FastAPI
from auth import router as auth_router
from file_processing import router as file_router

app = FastAPI()

# Include the routers
app.include_router(auth_router)
app.include_router(file_router)
