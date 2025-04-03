import json
import logging
import os
import uuid
from typing import Any, Dict, Optional

import azure.functions as func
from azure.monitor.opentelemetry import configure_azure_monitor

# Configure Azure Monitor only if we have the connection string
connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
if connection_string:
    configure_azure_monitor(
        connection_string=connection_string,
        disable_offline_storage=True,  # Ensure all telemetry is sent
        sampling_ratio=1.0,  # Sample 100% of telemetry
    )


class AppInsightsLoggerAdapter(logging.LoggerAdapter):
    """Custom LoggerAdapter that properly formats custom dimensions for App Insights."""

    def _convert_to_string(self, value: Any) -> str:
        """Convert any value to a string format suitable for custom dimensions."""
        if isinstance(value, (dict, list)):
            return json.dumps(value)
        return str(value)

    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple[str, Dict[str, Any]]:
        """Process the logging message and kwargs to inject custom dimensions."""
        # Initialize or get existing custom dimensions
        if "extra" not in kwargs:
            kwargs["extra"] = {}
        if "custom_dimensions" not in kwargs["extra"]:
            kwargs["extra"]["custom_dimensions"] = {}

        # Convert all values in custom dimensions to strings
        custom_dims = kwargs["extra"]["custom_dimensions"]
        kwargs["extra"]["custom_dimensions"] = {
            k: self._convert_to_string(v) for k, v in custom_dims.items()
        }

        # Add our context (like request_id) to custom dimensions, converting to strings
        if self.extra:
            kwargs["extra"]["custom_dimensions"].update(
                {k: self._convert_to_string(v) for k, v in self.extra.items()}
            )

        return msg, kwargs


def setup_logger(name: str = "resumematchpro") -> logging.Logger:
    """Initialize a logger with the given name.

    Ensures logs propagate to the root logger for OpenTelemetry to pick them up,
    while maintaining our custom logger hierarchy for organization.
    """
    # Get the root logger first - this is what OpenTelemetry hooks into
    root_logger = logging.getLogger()

    # Get our custom logger
    logger = logging.getLogger(name)

    # Ensure logs propagate up to root
    logger.propagate = True

    return logger


def get_logger_with_context(
    request_id: Optional[str] = None, blueprint_name: Optional[str] = None
) -> logging.Logger:
    """Get a logger instance with optional request context and blueprint name."""
    # Use blueprint name if provided, otherwise use default
    logger_name = (
        f"resumematchpro.{blueprint_name}" if blueprint_name else "resumematchpro"
    )
    logger = logging.getLogger(logger_name)

    # Add request ID to log context if provided
    if request_id:
        extra = {"request_id": request_id}
        logger = AppInsightsLoggerAdapter(logger, extra)

    return logger


def get_request_id(req: func.HttpRequest) -> str:
    """Extract or generate request ID for tracking."""
    return req.headers.get("x-ms-request-id") or str(uuid.uuid4())


# Create a singleton logger instance for application-wide logging
logger = setup_logger()
