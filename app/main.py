from fastapi import FastAPI
from app.api import speaking, listening, reading, writing

app = FastAPI(title='CleFluence', versin = "0.1.0")

app.include_router(speaking.router)
app.include_router(listening.router)
app.include_router(reading.router)
app.include_router(writing.router)