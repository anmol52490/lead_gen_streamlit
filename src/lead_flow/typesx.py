from typing import List

from pydantic import BaseModel


class Activity_Analyser(BaseModel):
    active: int


class Profile_Analyser(BaseModel):
    summary_profile: str


class Content_Analyst(BaseModel):
    summary_content: str

class Alignment(BaseModel):
    Alignment: str