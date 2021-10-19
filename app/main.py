from fastapi import FastAPI
from .routers import pigeon

app = FastAPI()
app.include_router(pigeon.router)

