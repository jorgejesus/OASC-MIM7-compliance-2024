from pydantic import BaseModel

# /ping
class PingResponse(BaseModel):
    status: str
    uptime: str
    startup_time: str
    current_time: str