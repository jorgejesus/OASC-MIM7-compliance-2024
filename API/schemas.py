from pydantic import BaseModel
from typing import Optional


# /ping
class PingResponse(BaseModel):
    status: str
    uptime: str
    startup_time: str
    current_time: str


# /r1
class ComplianceResponse(BaseModel):
    service_url: str
    status: str
    details: str


# /r2
class GeoPackageResponse(BaseModel):
    layer_name: str
    contains_geospatial_data: bool
    identifiers_unique: bool
    identifiers_persistent: bool
    message: Optional[str] = (
        None  # Optional message in case of an error or no data found
    )
