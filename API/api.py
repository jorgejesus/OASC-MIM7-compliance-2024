# check_service('https://geoserver.epsilon-italia.it/geoserver/LU_sample/ows) --> WFS 2.0.0 compliant
# check_service('https://demo.pygeoapi.io/stable/') --> OGC API features complainet
# check_service('https://www.google.com') --> Not compliant

# curl -X POST "http://127.0.0.1:8000/r2" -H "accept: application/json" \
#    -H "Content-Type: multipart/form-data" \
#    -F "file=@./tests/example.gpkg" \
import httpx
import os
from datetime import datetime; startup_time = datetime.now()

from fastapi import FastAPI, Query, Request, File, UploadFile
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from schemas import PingResponse, ComplianceResponse, GeoPackageResponse

from contextlib import asynccontextmanager
from config import LOG_LEVEL

from api_logging import log, request_id_var, log_requests
from api_exceptions import ComplianceException

import geopandas as gpd  # To read the GPKG layers
import pyogrio  # Vectorized spatial vector file format I/O using GDAL/OGR, with async support ???

import asyncio  # so that check_geopackage doesn't block the main event loop


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code to execute on startup
    await log.info("Startup Event fired")
    await log.info(f"Log level: {LOG_LEVEL}")

    yield

    # Code to execute on shutdown (optional)
    await log.info("API Shutdown Event fired")


app = FastAPI(lifespan=lifespan)


# This is due to the fact that if a server is not compliant the REST API (/r1), has to return
# 422 Unprocessable Entity
@app.exception_handler(ComplianceException)
async def compliance_exception_handler(request: Request, exc: ComplianceException):
    return JSONResponse(
        status_code=422,
        content={
            "service_url": exc.service_url,
            "status": exc.status,
            "details": exc.details,
        },
    )


@app.post("/r2")
async def check_geopackage(file: UploadFile = File(...)):
    """
    Check GeoPackage directly from the uploaded file without saving to a temporary location.

    curl -X POST "http://127.0.0.1:8000/r2" -H "accept: application/json"
    -H "Content-Type: multipart/form-data"
    -F "file=@./tests/example.gpkg"
    """
    # Check if file was uploaded
    if not file:
        raise HTTPException(status_code=400, detail="No file part")

    # Read the file directly from the UploadFile object
    file_content = await file.read()  # Read file content into memory

    # Offload the blocking function to a thread, pass file content as bytes
    result = await asyncio.to_thread(check_geopackage_func, file_content)

    # No need for JSONResponse; FastAPI will handle the serialization of Pydantic models
    return result
    # return JSONResponse(content=result)


def check_geopackage_func(file_content) -> GeoPackageResponse:
    """
    Check the GeoPackage file content passed as bytes.
    """
    try:
        # Load layers using pyogrio directly from in-memory bytes
        layers_info = pyogrio.list_layers(file_content)

        # Iterate over all layers
        for layer_info in layers_info:
            layer_name = layer_info[0]

            # Load the layer into a GeoDataFrame from the bytes content using geopandas
            data = gpd.read_file(file_content, layer=layer_name)

            if "geometry" in data.columns and not data["geometry"].isnull().all():
                data = data.head(50)  # Limit to 50 records

                # Return an actual GeoPackageResponse object
                return GeoPackageResponse(
                    layer_name=layer_name,
                    contains_geospatial_data=True,
                    identifiers_unique=data.index.is_unique,
                    identifiers_persistent=data.index.is_monotonic_increasing,
                )

    except Exception as e:
        return {"message": f"Error processing GeoPackage: {e}"}

    return {"message": "No geospatial data found in any layer"}


@app.get("/r1", response_model=ComplianceResponse)
async def check_service(
    url: str = Query(..., description="The URL of the service to check")
) -> ComplianceResponse:
    """
    Check remote services for complience.
    """

    # TODO validate that it was requested an URL
    wfs_url = f"{url}?SERVICE=WFS&REQUEST=GetCapabilities&VERSION=2.0.0"
    await log.info(f"Checking WFS service:{wfs_url}")

    async with httpx.AsyncClient() as client:
        try:
            wfs_response = await client.get(wfs_url)
            # TODO use owslib to make the request, parse and determine that it is ok
            await log.debug(f"WFS Response received:{wfs_response.text}")
            if (
                wfs_response.status_code == 200
                and "WFS_Capabilities" in wfs_response.text
            ):
                # Return a ComplianceResponse object
                return ComplianceResponse(
                    service_url=url,
                    status="compliant",
                    details="The service is a valid MIM-7 OGC WFS service.",
                )

            ogc_response = await client.get(url)
            await log.info("OGC Response received", response=ogc_response.text)
            # Server has rest end point f"{url}/conformance"
            if ogc_response.status_code == 200:
                conformance_url = f"{url}/conformance"
                conformance_response = await client.get(conformance_url)

                if conformance_response.status_code == 200:
                    return ComplianceResponse(
                        service_url=url,
                        status="compliant",
                        details="The service is a valid MIM-7 OGC API Features service.",
                    )
            # If service is not compliant, raise the custom ComplianceException
            else:
                raise ComplianceException(
                    service_url=url,
                    status="non-compliant",
                    details="The service is not a valid MIM-7 standards-based web service interface.",
                )
        except httpx.RequestError as exc:
            log.error(f"An error occurred while checking the service: {exc}")
            # Return HTTP 400 if the service cannot be reached, also with a structured response
            raise HTTPException(
                status_code=400,
                detail=ComplianceResponse(
                    service_url=url,
                    status="error",
                    details="Unable to contact the service. Check the URL.",
                ).dict(),
            )


@app.get("/ping", response_model=PingResponse)
async def ping_pong() -> PingResponse:
    """
    Ping the API to check if it is operational and report its uptime.
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

    # Starts HiperMilho event loop
    asyncio.run(serve(app, config))
