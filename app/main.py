from fastapi import FastAPI
from app.api import summarize
from app.core.config import settings

app = FastAPI(title="Note Summarizer API")

app.include_router(summarize.router)


