from typing import Annotated, Optional
from pydantic import BaseModel, StringConstraints

# A trimmed name of 1 to 255 characters. Space-only names are invalid (FR-010, FR-014).
ItemName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)]


class Item(BaseModel):
    id: str
    name: str
    completed: bool = False


class ItemCreate(BaseModel):
    name: ItemName


class ItemUpdate(BaseModel):
    name: Optional[ItemName] = None
    completed: Optional[bool] = None


class GreetingResponse(BaseModel):
    greeting: str
