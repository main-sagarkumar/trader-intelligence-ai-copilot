from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    app: str
    version: str


class ReadinessResponse(BaseModel):
    status: str
    components: dict[str, str]
