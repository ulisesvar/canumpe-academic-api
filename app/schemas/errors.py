from pydantic import BaseModel, ConfigDict


class ErrorResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {"error": "unauthorized", "message": "Invalid or missing API key"}
        }
    )

    error: str
    message: str
