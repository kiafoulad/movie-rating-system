from typing import Any, Optional

from pydantic import BaseModel


class ErrorDetail(BaseModel):
    """
    Represents error details in a failed API response.
    """

    code: int
    message: str


class APIResponse(BaseModel):
    """
    Generic API response model.

    - On success: status="success", data is not None, error=None
    - On failure: status="failure", data=None, error is not None
    """

    status: str
    data: Optional[Any] = None
    error: Optional[ErrorDetail] = None
