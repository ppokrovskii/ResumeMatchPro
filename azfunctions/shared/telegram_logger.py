import asyncio
import json
import logging
import os
import traceback
from datetime import datetime
from http import HTTPStatus
from typing import Any, Dict, Optional

import aiohttp
import requests
from azure.functions import HttpRequest

from .logger import AppInsightsLoggerAdapter, get_logger_with_context


class TelegramWebhookHandler(logging.Handler):
    """Custom logging handler that sends logs to Telegram via Azure Function webhook."""

    def __init__(self, webhook_url: Optional[str] = None):
        """Initialize the handler with webhook URL."""
        super().__init__()
        self.webhook_url = webhook_url or os.getenv("TELEGRAM_WEBHOOK_URL")
        if not self.webhook_url:
            raise ValueError("TELEGRAM_WEBHOOK_URL environment variable is required")

        # Only handle ERROR and CRITICAL levels
        self.setLevel(logging.ERROR)

        # Get a logger for the handler itself
        self.logger = get_logger_with_context(blueprint_name="telegram_handler")

    def format_exception(self, record: logging.LogRecord) -> Dict[str, Any]:
        """Format the exception information into a structured dictionary."""
        exc_info = record.exc_info
        if exc_info:
            exc_type, exc_value, exc_tb = exc_info
            tb_list = traceback.extract_tb(exc_tb)
            formatted_tb = []

            for tb in tb_list:
                formatted_tb.append(
                    {
                        "filename": tb.filename,
                        "line": tb.lineno,
                        "function": tb.name,
                        "text": tb.line,
                    }
                )

            return {
                "exception_type": exc_type.__name__ if exc_type else None,
                "exception_message": str(exc_value) if exc_value else None,
                "traceback": formatted_tb,
            }
        return {}

    def format_record(self, record: logging.LogRecord) -> Dict[str, Any]:
        """Format the log record into a structured dictionary."""
        data = {
            "level": record.levelname,
            "logger_name": record.name,
            "message": record.getMessage(),
            "timestamp": record.created,
            "function": record.funcName,
            "line_number": record.lineno,
            "file_path": record.pathname,
        }

        # Add exception info if present
        if record.exc_info:
            data["exception"] = self.format_exception(record)

        # Add custom dimensions if present
        if hasattr(record, "custom_dimensions"):
            data["custom_dimensions"] = record.custom_dimensions

        return data

    def emit(self, record: logging.LogRecord) -> None:
        """Send the log record to the Telegram webhook."""
        try:
            # Format the record
            data = self.format_record(record)

            # Send to webhook
            response = requests.post(
                self.webhook_url,
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=5,  # 5 seconds timeout
            )

            # Log the result
            if response.status_code != HTTPStatus.OK:
                self.logger.error(
                    "Failed to send log to Telegram webhook",
                    extra={
                        "custom_dimensions": {
                            "status_code": response.status_code,
                            "response_text": response.text,
                            "log_data": json.dumps(data),
                        }
                    },
                )
        except Exception as e:
            self.logger.exception(
                "Error sending log to Telegram webhook",
                extra={"custom_dimensions": {"error": str(e)}},
            )


def setup_telegram_logger(name: str = "resumematchpro") -> logging.Logger:
    """Set up a logger with Telegram webhook handler."""
    logger = logging.getLogger(name)

    # Add Telegram webhook handler
    telegram_handler = TelegramWebhookHandler()
    telegram_handler.setLevel(logging.ERROR)
    logger.addHandler(telegram_handler)

    return logger


class AsyncTelegramWebhookHandler(logging.Handler):
    """
    A custom logging handler that asynchronously sends log messages to a Telegram webhook.
    """

    def __init__(self, function_app_name: str, min_level: int = logging.ERROR):
        """
        Initialize the handler.

        Args:
            function_app_name: The name of your Azure Function App
            min_level: Minimum logging level to send to Telegram (default: ERROR)
        """
        super().__init__(level=min_level)
        self.webhook_url = (
            f"https://{function_app_name}.azurewebsites.net/api/telegram-webhook"
        )
        self.session: Optional[aiohttp.ClientSession] = None
        self.loop = asyncio.get_event_loop()

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    def format_message(self, record: logging.LogRecord) -> Dict[str, Any]:
        """Format the log record into a message for Telegram."""
        timestamp = datetime.fromtimestamp(record.created).isoformat()

        # Extract custom dimensions if available
        custom_dimensions = getattr(record, "custom_dimensions", {})
        if hasattr(record, "extra") and isinstance(record.extra, dict):
            custom_dimensions.update(record.extra.get("custom_dimensions", {}))

        message = {
            "schemaId": "azureMonitorCommonAlertSchema",
            "data": {
                "essentials": {
                    "alertId": custom_dimensions.get("request_id", ""),
                    "alertRule": f"Custom Logger Alert - {record.levelname}",
                    "severity": "Error"
                    if record.levelno >= logging.ERROR
                    else "Warning",
                    "signalType": "Log",
                    "monitorCondition": "Fired",
                    "monitorService": "Custom Logger",
                    "targetResource": os.getenv("WEBSITE_SITE_NAME", "Unknown"),
                    "timestamp": timestamp,
                },
                "customProperties": {
                    "LogLevel": record.levelname,
                    "Logger": record.name,
                    "Message": record.getMessage(),
                    "StackTrace": "".join(traceback.format_exception(*record.exc_info))
                    if record.exc_info
                    else None,
                    "custom_dimensions": json.dumps(custom_dimensions),
                },
            },
        }
        return message

    async def _emit_async(self, record: logging.LogRecord):
        """Asynchronously emit the log record."""
        try:
            session = await self._get_session()
            message = self.format_message(record)

            async with session.post(self.webhook_url, json=message) as response:
                if response.status not in (200, 201, 202):
                    print(f"Failed to send log to Telegram webhook: {response.status}")

        except Exception as e:
            print(f"Error sending log to Telegram webhook: {e}")

    def emit(self, record: logging.LogRecord):
        """Emit the log record by scheduling it in the event loop."""
        asyncio.run_coroutine_threadsafe(self._emit_async(record), self.loop)


def add_telegram_handler(
    logger: logging.Logger, function_app_name: str, min_level: int = logging.ERROR
):
    """
    Add the Telegram webhook handler to an existing logger.

    Args:
        logger: The logger to add the handler to
        function_app_name: The name of your Azure Function App
        min_level: Minimum logging level to send to Telegram (default: ERROR)
    """
    handler = AsyncTelegramWebhookHandler(function_app_name, min_level)
    logger.addHandler(handler)
    return logger
