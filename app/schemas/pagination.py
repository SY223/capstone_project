from typing import Generic, List, TypeVar
from pydantic import BaseModel, ConfigDict

T = TypeVar("T")

class PaginatedResult(BaseModel, Generic[T]):
    total: int
    skip: int
    limit: int
    items: List[T]

    model_config = ConfigDict(from_attributes=True)