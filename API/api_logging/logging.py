import structlog
import rich.console
import rich.logging
from ulid import ULID
import logging
import contextvars
from config import LOG_LEVEL
from fastapi import Request

# Set up Rich Console, for nice colours for easy tracking of problems
console = rich.console.Console()
rich_handler = rich.logging.RichHandler(console=console, show_time=True, show_level=True, show_path=False)

# Configure standard logging to use RichHandler
logging.basicConfig(level=LOG_LEVEL, format="%(message)s", handlers=[rich_handler])

# Context variable, ya sync debug is not easy
request_id_var = contextvars.ContextVar("request_id", default=None)

# Configure structlog
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.ExceptionPrettyPrinter(),
        structlog.processors.UnicodeDecoder(),
        structlog.processors.KeyValueRenderer(key_order=["event", "logger"]),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.stdlib.AsyncBoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True, # Start log caching improves performance
)

# Integrate Structlog with the standard logging module
log = structlog.get_logger()

async def log_requests(request: Request, call_next):
    """
    Middleware to log incoming HTTP requests and responses with a unique request ID.

    This middleware performs the following tasks:
    - Generates a unique request ID using ULID for each incoming HTTP request.
    - Sets a context variable with the request ID for consistent logging.
    - Logs the details of incoming requests, including the HTTP method and URL.
    - Proceeds to the next middleware or route handler and logs the response status code.
    - Catches and logs HTTP exceptions with the status code and details.
    - Catches and logs any unexpected exceptions, then re-raises them for FastAPI's error handling.

    Args:
        request (Request): The incoming HTTP request object.
        call_next (Callable): The next middleware or route handler to be called. Check fastapi docs for better explanations

    Returns:
        Response: The HTTP response object after processing by the next middleware or route handler.

    Example:
        When a request is received, the following logs might be generated:
        - "Request received", method="GET", url="/ping", request_id="01FZ8TZC9S6M6V3A1XJY2HY7D8"
        - "Response sent", status_code=200, request_id="01FZ8TZC9S6M6V3A1XJY2HY7D8"
    
    Raises:
        HTTPException: If an HTTP-specific exception occurs during request processing.
        Exception: Any other unexpected exception that might occur during request processing.
    """
    # Generate a unique request ID using ULID
    
    request_id = str(ULID())
    # Set context variable for this request
    request_id_var.set(request_id)

    try:
        # Log request with context
        await log.debug(
            "Request received",
            method=request.method,
            url=str(request.url),
            request_id=request_id_var.get(),
        )

        # Call the next middleware or route handler
        response = await call_next(request)

        # Log response with context
        await log.debug(
            "Response sent",
            status_code=response.status_code,
            request_id=request_id_var.get(),
        )
        return response

    except HTTPException as exc:
        # Handle and log HTTP exceptions specifically
        await log.error(
            f"HTTP Exception occurred: {exc.detail}",
            status_code=exc.status_code,
            request_id=request_id_var.get(),
        )
        return JSONResponse(content={"detail": exc.detail}, status_code=exc.status_code)

    except Exception as e:
        # Handle any other exceptions
        await log.error(
            f"An unexpected error occurred: {str(e)}", request_id=request_id_var.get()
        )
        raise  # Reraise to ensure FastAPI's error handling kicks in

