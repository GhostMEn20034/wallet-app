from pydantic import BaseModel, Field
from typing import List
from .users import PyObjectId


class Subcategory(BaseModel):
    name: str


class Category(BaseModel):
    id: PyObjectId = Field(alias="_id")
    name: str
    subcategories: List[Subcategory]
