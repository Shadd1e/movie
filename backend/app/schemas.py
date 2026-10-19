from typing import Literal

from pydantic import BaseModel, Field, field_validator

AgeGroup = Literal["60–69", "70–79", "80+"]
MovieYearPreference = Literal[
    "before_1980",
    "1980_1999",
    "2000_2009",
    "2010_2019",
    "2020_onwards",
]


class ProfileFields(BaseModel):
    name: str | None = Field(default=None, max_length=100)
    age_group: AgeGroup | None = None
    region: str | None = Field(default=None, max_length=100)
    country: str | None = Field(default=None, max_length=100)
    genres: list[str] = Field(default_factory=list, max_length=12)
    favourite_movie_ids: list[int] = Field(default_factory=list, max_length=10)
    preferred_movie_years: list[MovieYearPreference] = Field(default_factory=list, max_length=5)

    @field_validator("name", "region", "country")
    @classmethod
    def trim_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None

    @field_validator("genres")
    @classmethod
    def clean_genres(cls, values: list[str]) -> list[str]:
        cleaned = []
        seen = set()
        for value in values:
            item = value.strip()
            if item and item.casefold() not in seen:
                cleaned.append(item)
                seen.add(item.casefold())
        return cleaned


class Onboarding(ProfileFields):
    pass


class Rating(BaseModel):
    movie_id: int = Field(gt=0)
    rating: float = Field(ge=1, le=5)


class SearchQuery(BaseModel):
    q: str = Field(min_length=1, max_length=100)


class NaturalRequest(BaseModel):
    request: str = Field(min_length=3, max_length=500)
