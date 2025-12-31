class APIError(Exception):
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


class NotFoundError(APIError):
    def __init__(self, message: str = "Not found"):
        super().__init__(404, message)


class BadRequestError(APIError):
    def __init__(self, message: str = "Bad request"):
        super().__init__(400, message)


class UnprocessableEntityError(APIError):
    def __init__(self, message: str = "Validation error"):
        super().__init__(422, message)
