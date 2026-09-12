from fastapi import HTTPException


class ApiError(HTTPException):
    """An HTTPException whose detail is already shaped for the public error contract.

    Produces {"error": "<slug>", "message": "<human readable>"} in the response body.
    """

    def __init__(self, status_code: int, error: str, message: str) -> None:
        super().__init__(status_code=status_code, detail={"error": error, "message": message})


def unauthorized(message: str = "Invalid or missing API key") -> ApiError:
    return ApiError(status_code=401, error="unauthorized", message=message)
