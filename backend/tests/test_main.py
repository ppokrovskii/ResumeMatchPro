def test_get_message():
    from application.main import get_message
    assert get_message() == {"message": "Hello World"}
