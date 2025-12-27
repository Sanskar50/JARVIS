from pydantic import BaseModel, Field
from typing import Optional, List

class WeatherToolInput(BaseModel):
    location: str = Field(..., description="The city and state, e.g. San Francisco, CA")
    unit: Optional[str] = Field("celsius", description="Unit of temperature")

class DBQueryInput(BaseModel):
    query: str = Field(..., description="SQL query to execute")

class WebSearchInput(BaseModel):
    query: str = Field(..., description="Search query string")
