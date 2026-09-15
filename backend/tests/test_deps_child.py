from app.security import create_token, decode_token


def test_child_token_type_is_child():
    token = create_token(subject="5", token_type="child")
    payload = decode_token(token)
    assert payload["type"] == "child"
    assert payload["sub"] == "5"
