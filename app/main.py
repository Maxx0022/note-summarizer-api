import os
from fastapi import FastAPI
from pydantic import BaseModel, AnyHttpUrl
from newspaper import Article
from openai import OpenAI
from dotenv import load_dotenv

app = FastAPI(title="Website Summarizer API")


load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
openAI_client = OpenAI(api_key=openai_api_key)  # noqa: N816


class LinkInput(BaseModel):
    link: AnyHttpUrl


class Summary(BaseModel):
    link: str
    text: str
    text_summary: str


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



@app.post("/summarize", response_model=Summary)
async def summarize(link_input: LinkInput):
    url_str = str(link_input.link)
    article = Article(url_str)
    article.download()
    article.parse()
    summary_text = get_openAI_summarization(article.text)

    return Summary(link=url_str, text=article.text, text_summary=summary_text)
