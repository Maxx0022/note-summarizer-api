from sqlmodel import SQLModel, Field

class Summary(SQLModel, table=True):
    id: int | None = Field(primary_key=True, index=True)
    link: str
    text: str
    text_summary: str