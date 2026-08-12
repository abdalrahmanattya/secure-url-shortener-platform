import pytest

from secure_shortener.validation import validate_destination


@pytest.mark.parametrize(
    "url",
    [
        "ftp://example.com",
        "http://localhost/x",
        "http://127.0.0.1/x",
        "https://user:pass@example.com/x",
    ],
)
def test_rejects_unsafe_destinations(url):
    with pytest.raises(ValueError):
        validate_destination(url)


def test_resolver_is_injectable_and_requires_global_addresses():
    assert (
        validate_destination("https://example.test/path", lambda _: ["93.184.216.34"])
        == "https://example.test/path"
    )
    with pytest.raises(ValueError):
        validate_destination("https://example.test/path", lambda _: ["10.0.0.1"])
    with pytest.raises(ValueError):
        validate_destination("https://example.test/path", lambda _: [])
