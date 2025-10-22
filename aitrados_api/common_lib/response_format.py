import json
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





class WsUnifiedResponse(UnifiedResponse):
    message_type: str

class WsErrorResponse(ErrorResponse):
    message_type: str

def get_standard_response(data:str|dict|UnifiedResponse|ErrorResponse|WsUnifiedResponse|WsErrorResponse)->UnifiedResponse|ErrorResponse|WsUnifiedResponse|WsErrorResponse:
    if isinstance(data,UnifiedResponse|ErrorResponse|WsUnifiedResponse|WsErrorResponse):
        return data
    try:
        if isinstance(data, str):
            data=json.loads(data)
        if isinstance(data, dict):
            for cls in [UnifiedResponse,ErrorResponse,WsUnifiedResponse,WsErrorResponse]:
                try:
                    return cls(**data)
                except:
                    pass


    except:
        return None



