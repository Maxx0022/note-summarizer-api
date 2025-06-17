from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, AnyHttpUrl

app = FastAPI(title="Note Summarizer API")


class LinkInput(BaseModel):
    link: AnyHttpUrl


class Summary(BaseModel):
    link: AnyHttpUrl
    text: str
    text_summary: str


@app.post("/summarize", response_model=Summary)
def summarize(link_input: LinkInput):
    
