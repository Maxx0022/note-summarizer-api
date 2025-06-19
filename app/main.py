import os
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, AnyHttpUrl
from newspaper import Article
from openai import OpenAI
from dotenv import load_dotenv
from sqlmodel import Session, select
from .models.summaries import Summary
from .db.database import get_session, init_db, reset_db

app = FastAPI(title="Website Summarizer API")


load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
openAI_client = OpenAI(api_key=openai_api_key)  # noqa: N816

reset_db()
init_db()


class LinkInput(BaseModel):
    link: AnyHttpUrl


class TextInput(BaseModel):
    text: str


def get_openAI_summarization(article_text: str) -> str:  # noqa: N802
    system_prompt = "You are a helpful assistant that summarizes long articles clearly and concisely for a general audience."

    user_prompt = (
        "Summarize the following article in a concise and informative way. "
        "Avoid unnecessary details and focus on the key points:\n\n"
        f"{article_text}"
    )
    response = openAI_client.responses.create(
        model="gpt-4o-mini",
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.output_text


@app.post("/summarize/link", response_model=Summary)
def summarize(link_input: LinkInput, session: Session = Depends(get_session)):  # noqa: B008
    url_str = str(link_input.link)

    stored_summary = session.exec(select(Summary).where(Summary.link == url_str)).first()

    if stored_summary:
        return stored_summary

    article = Article(url_str)
    article.download()
    article.parse()
    summary_text = get_openAI_summarization(article.text)
    summary = Summary(link=url_str, text=article.text, text_summary=summary_text)

    session.add(summary)
    session.commit()
    session.refresh(summary)

    return summary


@app.get("/summarization/{summarization_id}", response_model=Summary)
def get_summary(summarization_id: int, session: Session = Depends(get_session)):  # noqa: B008
    summarization = session.get(Summary, summarization_id)
    if not summarization:
        raise HTTPException(status_code=404, detail="summarization not found")
    return summarization


@app.post("/summarize/text", response_model=Summary)
def get_text_summary(text_input: TextInput, session: Session = Depends(get_session)):
    text_summary = get_openAI_summarization(text_input.text)
    summary = Summary(link=None, text=text_input.text, text_summary=text_summary)

    session.add(summary)
    session.commit()
    session.refresh(summary)

    return summary
