from pydantic import BaseModel


class DirectorOut(BaseModel):
    id: int
    name: str
    birth_year: int | None = None
    description: str | None = None
