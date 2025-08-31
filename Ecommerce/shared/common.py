from typing import Generic, TypeVar, Optional

T = TypeVar("T")

class ResponseGlobal(Generic[T]):
    def __init__(self, 
        success: bool = False, 
        message: str = '', 
        error: str = '', 
        data: Optional[T] = None):
        self.success = success
        self.message = message
        self.error = error
        self.data = data

    def to_dict(self) -> dict:
       
        return {
            "success": self.success,
            "message": self.message,
            "error": self.error,
            "data": self.data
        }
