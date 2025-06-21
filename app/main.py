import os
from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, AnyHttpUrl, Field
from newspaper import Article
from trafilatura import fetch_url, extract
from openai import OpenAI
from dotenv import load_dotenv
from sqlmodel import Session, select
from .models.summaries import Summary
from .db.database import get_session, init_db

app = FastAPI(title="Website Summarizer API")


load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
openAI_client = OpenAI(api_key=openai_api_key)  # noqa: N816
init_db()


class LinkInput(BaseModel):
    link: AnyHttpUrl
    length_index: Annotated[int, Field(strict=True, gt=0, le=10)]


class TextInput(BaseModel):
    text: str
    length_index: Annotated[int, Field(strict=True, gt=0, le=10)]


def get_newspaper3k_extraction(url):
    article = Article(url)
    article.download()
    article.parse()
    return article

def get_trafilatura_extraction(url):
    downloaded_article = fetch_url(url)
    return extract(downloaded_article)

LENGTH_INDEX_MODEL = {
    1: "Summarize this input in 1-2 sentences.",
    2: "Summarize this input in 3-4 sentences.",
    3: "Summarize this input in a short paragraph.",
    4: "Summarize this input in a detailed paragraph.",
    5: "Summarize this input in a detailed multi-paragraph summary.",
    6: "Summarize this input with extensive detail and examples.",
    7: "Summarize this input in a thorough multi-paragraph explanation.",
    8: "Summarize this input with in-depth analysis.",
    9: "Summarize this input in a comprehensive report style.",
    10: "Summarize this input in a full-length detailed article."
}


def get_openAI_summarization(article_text: str, length_index: int) -> str:  # noqa: N802
    system_prompt = "You are a helpful assistant that summarizes long articles clearly and concisely for a general audience."

    few_shots = [
        {
            "role": "user",
            "content": (
                "Summarize the following article in a concise and informative way. "
                "Avoid unnecessary details and focus on the key points:\n\n"
                "The European Central Bank (ECB) raised interest rates by 0.25% on Thursday to combat persistently high inflation. "
                "This move marks the tenth consecutive rate hike, pushing borrowing costs to their highest levels in over two decades. "
                "Despite slowing economic growth in the eurozone, ECB President Christine Lagarde emphasized that inflation remains too high."
            ),
        },
        {
            "role": "assistant",
            "content": (
                "The ECB raised interest rates for the tenth time, aiming to curb high inflation despite slowing economic growth in the eurozone. "
                "President Lagarde reaffirmed the central bank's commitment to tackling inflation."
            ),
        },
        {
            "role": "user",
            "content": (
                "Summarize the following article in a concise and informative way. "
                "Avoid unnecessary details and focus on the key points:\n\n"
                "NASA announced a new mission to explore Jupiter's moon Europa, a promising candidate in the search for extraterrestrial life. "
                "Scheduled for launch in 2026, the Europa Clipper spacecraft will investigate the moon's icy shell and subsurface ocean. "
                "The mission aims to determine if the moon harbors the necessary conditions for life."
            ),
        },
        {
            "role": "assistant",
            "content": (
                "NASA is launching the Europa Clipper in 2026 to explore Jupiter's moon Europa, focusing on its icy surface and subsurface ocean "
                "to assess its potential to support life."
            ),
        },
    ]

    user_prompt = {
        "role": "user",
        "content": (
            "Summarize the following article in a concise and informative way. You should return the text in the same language as sent to you in the input. "
            f"{LENGTH_INDEX_MODEL.get(length_index)} "
            "Avoid unnecessary details and focus on the key points:\n\n"
            f"{article_text}"
        ),
    }

    response = openAI_client.responses.create(
        model="gpt-4o-mini",
        input=[
            {"role": "system", "content": system_prompt},
            *few_shots,
            user_prompt,
        ], # type: ignore
    )
    return response.output_text


@app.post("/summarize-link", response_model=Summary)
def summarize(link_input: LinkInput, session: Session = Depends(get_session)):  # noqa: B008
    url_str = str(link_input.link)

    stored_summary = session.exec(select(Summary).where(Summary.link == url_str)).first()

    # if stored_summary:
    #     return stored_summary

    article = get_trafilatura_extraction(url_str)
    if not article:
        print("trafilatura extraction has failed, falling back to newspaper3k extraction...")
        article = get_newspaper3k_extraction(url_str).text

    summary_text = get_openAI_summarization(article, link_input.length_index)
    summary = Summary(link=url_str, text=article, text_summary=summary_text)

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


@app.post("/summarize-text", response_model=Summary)
def get_text_summary(text_input: TextInput, session: Session = Depends(get_session)):
    text_summary = get_openAI_summarization(text_input.text, text_input.length_index)
    summary = Summary(link=None, text=text_input.text, text_summary=text_summary)

    session.add(summary)
    session.commit()
    session.refresh(summary)

    return summary
