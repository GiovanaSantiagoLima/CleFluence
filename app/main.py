from fastapi import FastAPI
from app.routers import content, progress, user

app = FastAPI(title='CleFluence', versin = "0.1.0")

app.include_router(content.router)
app.include_router(progress.router)
app.include_router(user.router)
