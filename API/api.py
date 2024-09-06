
from api_logging.logging import log, request_id_var, log_requests
from fastapi import FastAPI, Query, UploadFile, File, HTTPException 
from contextlib import asynccontextmanager
from schemas import PingResponse
from config import LOG_LEVEL
import httpx
import os
from datetime import datetime

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code to execute on startup
    await log.info("Startup Event fired")
    await log.info(f"Log level: {LOG_LEVEL}")

    yield

    # Code to execute on shutdown (optional)
    await log.info("API Shutdown Event fired")

app = FastAPI(lifespan=lifespan)

@app.get("/ping", response_model=PingResponse)
async def ping_pong() -> PingResponse:
    """
    Ping the system to check if it is operational and report its uptime.
    """
    current_time = datetime.now()
    uptime = current_time - startup_time
    # NO microseconds
    uptime_str = str(uptime).split(".")[0]
    startup_time_iso = startup_time.isoformat()
    current_time_iso = current_time.isoformat()
    # Dummy status as operations, extend status are necessary
    return PingResponse(
        status="operational",
        uptime=uptime_str,
        startup_time=startup_time_iso,
        current_time=current_time_iso,
    )



# HyperCorn as HTTP2.0 server (HiperMilho)  
if __name__ == "__main__":
    # python api.py
    import asyncio
    from hypercorn.asyncio import serve
    from hypercorn.config import Config
    from fastapi import FastAPI

    config = Config()
    config.bind = ["0.0.0.0:8000"]
    # Starts hypercorn event loop
    asyncio.run(serve(app, config))
