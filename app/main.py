from fastapi import FastAPI
from .constants import APP_NAME
from .routes import root

app = FastAPI(title=APP_NAME, version="0.1.0")

app.include_router(root.router)
