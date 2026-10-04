from src.core.config import Settings


def test_cors_origins_parsed_from_comma_string() -> None:
    settings = Settings(CORS_ORIGINS="http://a.com, http://b.com")
    assert settings.CORS_ORIGINS == ["http://a.com", "http://b.com"]


def test_cors_origins_list_passthrough() -> None:
    settings = Settings(CORS_ORIGINS=["http://a.com"])
    assert settings.CORS_ORIGINS == ["http://a.com"]


def test_cors_origins_non_string_fallback() -> None:
    settings = Settings(CORS_ORIGINS=42)
    assert settings.CORS_ORIGINS == ["42"]
