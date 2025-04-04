import asyncio
import logging
import os
from typing import Optional

import aiohttp


class AsyncTelegramWebhookHandler(logging.Handler):
    """A custom logging handler that asynchronously sends log messages to a Telegram webhook."""

    def __init__(self, function_app_name: str, min_level: int = logging.ERROR):
        super().__init__(level=min_level)
        self.webhook_url = (
            f"https://{function_app_name}.azurewebsites.net/api/telegram-webhook"
        )
        self.session: Optional[aiohttp.ClientSession] = None
        self.loop = asyncio.get_event_loop()

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def _emit_async(self, record: logging.LogRecord):
        try:
            session = await self._get_session()
            # Format the record using the default formatter
            formatted_message = self.format(record)
            message = {"message": formatted_message}

            async with session.post(self.webhook_url, json=message) as response:
                if response.status not in (200, 201, 202):
                    print(f"Failed to send log to Telegram webhook: {response.status}")

        except Exception as e:
            print(f"Error sending log to Telegram webhook: {e}")

    def emit(self, record: logging.LogRecord):
        asyncio.run_coroutine_threadsafe(self._emit_async(record), self.loop)


def setup_logging():
    """
    Initialize application-wide logging configuration.
    This sets up both basic logging and Telegram logging if configured.
    """
    # Initialize basic logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Add Telegram handler to root logger if function name is available
    function_app_name = os.getenv("TELEGRAM_ALERT_FUNCTION_NAME")
    if function_app_name:
        # Create and add the Telegram handler
        handler = AsyncTelegramWebhookHandler(function_app_name)
        logging.getLogger().addHandler(handler)

    # Log application startup
    logging.info("Function app initialized with logging configuration")
