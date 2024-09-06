from pydantic import BaseModel


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
