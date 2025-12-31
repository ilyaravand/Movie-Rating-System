from pydantic import BaseModel


class GenreOut(BaseModel):
    id: int
    name: str
    description: str | None = None
