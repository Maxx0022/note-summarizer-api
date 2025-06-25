# Note-Summarizer-API

## Introduction

Thank you for taking the time to check out my open-source project.

This project, Note Summarizer API, is a FastAPI-based backend that allows users to summarize articles, raw text, or uploaded PDF/TXT files using OpenAI's GPT 4o-mini model. It can also export summaries as PDF files.

I started this project on June 16, 2025, with no prior experience using FastAPI. Since then, I’ve learned a lot and continue improving the app. If you spot anything that could be improved or see non-idiomatic code, please let me know so that i can improve it.

Please note: This project is a work in progress, and some features may still be under development.

## Getting started

1. Clone the repository

```
git clone git@github.com:Maxx0022/note-summarizer-api.git
```

2. Install dependencies using Poetry

- poetry install

Make sure you have Python 3.10+ and Poetry installed.

3. Create a `.env` file in the root directory and add your OpenAI API key + Database URI

```
OPENAI_API_KEY="your_openai_key_here"
PSQL_LINK="your_db_uri_here"
```

4. Start the development server

```
uvicorn app.main:app --reload
```

Once running, go to http://127.0.0.1:8000/docs to explore the API using the Swagger UI. You can also use tools like Postman.

## Features

- Summarize web links (via trafilatura or newspaper3k)
- Summarize raw text input
- Summarize uploaded PDF files
- Store summaries in a local database using SQLModel
- Export summaries as downloadable PDF files (UNSTABLE, WORK IN PROGRESS)
- Control summary length using a length_index field (1–10)

## Future plans

This project is still in development, and I plan to add:

- Improve PDF export stability and formatting
- .txt file summarization
- Authentication with JWT
- Rate limiting
- Dockerization
- A simple frontend interface
- Summarization tone/style options
