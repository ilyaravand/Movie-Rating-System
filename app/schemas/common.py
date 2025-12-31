from pydantic import BaseModel


class ErrorPayload(BaseModel):
    code: int
    message: str


class FailureResponse(BaseModel):
    status: str = "failure"
    error: ErrorPayload


class SuccessResponse(BaseModel):
    status: str = "success"
    data: object
