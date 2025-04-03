import logging
import warnings

import pytest
from shared.logger import (
    AppInsightsLoggerAdapter,
    get_logger_with_context,
    setup_logger,
)


def test_custom_dimensions_warning():
    """
    Test that custom dimensions are properly formatted to avoid warnings.
    This test reproduces the warning:
    'Invalid type dict for attribute 'custom_dimensions' value. Expected one of ['bool', 'str', 'bytes', 'int', 'float']'
    """
    # Create a logger
    logger = setup_logger("test_logger")

    # Create a handler that will actually try to send to App Insights
    handler = logging.StreamHandler()
    logger.addHandler(handler)

    # Capture warnings
    with warnings.catch_warnings(record=True) as warning_list:
        warnings.simplefilter("always")  # Ensure all warnings are captured

        # Create a logger with context that includes a dictionary
        context = {
            "request_id": "test-123",
            "user_id": "user-456",
            "nested": {
                "key": "value"
            },  # This should trigger the warning if not handled properly
        }

        # Get logger with context
        logger_with_context = get_logger_with_context(
            request_id=context["request_id"], blueprint_name="test_blueprint"
        )

        # Log a message
        logger_with_context.info("Test message", extra={"custom_dimensions": context})

        # Check for the specific App Insights warning
        app_insights_warnings = [
            str(w.message)
            for w in warning_list
            if "custom_dimensions" in str(w.message)
            and "Invalid type" in str(w.message)
        ]
        assert len(app_insights_warnings) == 0, (
            f"App Insights warnings found: {app_insights_warnings}"
        )


def test_app_insights_logger_adapter():
    """
    Test that AppInsightsLoggerAdapter properly formats custom dimensions.
    """
    # Create a base logger
    logger = logging.getLogger("test_adapter")
    logger.setLevel(logging.INFO)

    # Create a handler to capture logs
    log_capture = []
    handler = logging.Handler()
    handler.emit = lambda record: log_capture.append(record)
    logger.addHandler(handler)

    # Create adapter with complex context
    context = {
        "request_id": "test-123",
        "user_id": "user-456",
        "nested": {"key": "value"},
        "list": [1, 2, 3],
        "bool": True,
        "int": 42,
        "float": 3.14,
    }

    adapter = AppInsightsLoggerAdapter(logger, context)

    # Log a message
    adapter.info("Test message")

    # Get the last log record
    last_record = log_capture[-1]

    # Check that custom dimensions are properly formatted
    assert hasattr(last_record, "custom_dimensions"), (
        "Record should have custom_dimensions"
    )
    assert isinstance(last_record.custom_dimensions, dict), (
        "custom_dimensions should be a dict"
    )

    # Check that all values are properly converted to strings
    for key, value in last_record.custom_dimensions.items():
        assert isinstance(value, str), (
            f"Value for key '{key}' should be a string, got {type(value)}"
        )
