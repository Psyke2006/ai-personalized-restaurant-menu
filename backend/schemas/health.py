from pydantic import BaseModel

class HealthResponse(BaseModel):
    status: str
    version: str
    recommender_engine: str
