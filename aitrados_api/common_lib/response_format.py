from typing import TypeVar, Generic, Optional, Any

from pydantic import BaseModel

T = TypeVar('T')

class UnifiedResponse(BaseModel, Generic[T]):
    status: str = "ok"
    code: int = 200
    message: str = "success"
    reference: Optional[Any] = None
    result: Optional[T] = None

class ErrorResponse(BaseModel):
    status: str = "error"
    code: int = 400
    message: str
    reference: Optional[Any] = None
    detail: Optional[Any] = None