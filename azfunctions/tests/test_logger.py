import asyncio
import logging
import os
from unittest.mock import AsyncMock, patch

import pytest
from shared.logger import setup_logging


@pytest.mark.asyncio
@patch("aiohttp.ClientSession")
@patch.dict(os.environ, {"TELEGRAM_ALERT_FUNCTION_NAME": "test-function-app"})
async def test_telegram_logging_flow(mock_session_class):
    """
    Test the complete logging flow from setup to message sending.
    Verifies that messages are properly formatted and sent to Telegram.
    """
    # Setup mock session
    mock_session = AsyncMock()
    mock_session_class.return_value = mock_session
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_session.post.return_value = AsyncMock()
    mock_session.post.return_value.__aenter__.return_value = mock_response

    # Setup logging (this should create the Telegram handler)
    setup_logging()

    # Log a test message
    test_message = "Test message"
    logging.exception(test_message)

    # Wait for async operation to complete
    await asyncio.sleep(0.1)

    # Verify the message was sent with correct format
    mock_session.post.assert_called_once()
    call_args = mock_session.post.call_args[1]
    message = call_args["data"]

    # Check that the message contains all required components
    assert "root" in message
    assert "ERROR" in message
    assert test_message in message
    assert message.endswith(" - root - ERROR - Test message\nNoneType: None")
