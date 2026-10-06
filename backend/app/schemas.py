from pydantic import BaseModel, Field
from typing import Optional

class Onboarding(BaseModel):
    age_group: str | None = Field(default=None, pattern=r"^(60–69|70–79|80\+)$")
    genres: list[str] = Field(default_factory=list, max_length=12)
    favourite_movie_ids: list[int] = Field(default_factory=list, max_length=10)

class Rating(BaseModel):
    movie_id: int
    rating: float = Field(ge=1, le=5)

class SearchQuery(BaseModel):
    q: str = Field(min_length=1, max_length=100)

class NaturalRequest(BaseModel):
    request: str = Field(min_length=3, max_length=500)
