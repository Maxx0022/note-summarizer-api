from fastapi import FastAPI
from pydantic import BaseModel, AnyHttpUrl
from newspaper import Article
from transformers import pipelines

app = FastAPI(title="Website Summarizer API")


class LinkInput(BaseModel):
    link: AnyHttpUrl


class Summary(BaseModel):
    link: str
    text: str
    text_summary: str

@app.post("/summarize", response_model=Summary)
async def summarize(link_input: LinkInput):
    url_str = str(link_input.link)

    article = Article(url_str)
    article.download()
    article.parse()

    summarizer = pipelines.pipeline("summarization", model="facebook/bart-large-cnn")

    summarized_text = summarizer(article.text, max_length=150)
    print(summarized_text)
    return Summary(link=url_str, text=article.text, text_summary='summary here')
