"""验证生产环境的安全配置约束。"""

import pytest
from pydantic import ValidationError

from app.core.config import Settings

PRODUCTION_SETTINGS = {
    "ENVIRONMENT": "production",
    "DEBUG": False,
    "SECRET_KEY": "production-only-secret-key-with-32-characters",
    "DB_USER": "app",
    "DB_PASSWORD": "production-database-password",
    "BACKEND_CORS_ORIGINS": ["https://app.example.com"],
}


def test_valid_production_settings_are_accepted():
    settings = Settings(_env_file=None, **PRODUCTION_SETTINGS)

    assert settings.ENVIRONMENT == "production"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("DEBUG", True),
        ("SECRET_KEY", "change-me-to-a-random-secret-key-32chars-min"),
        ("DB_USER", "root"),
        ("DB_PASSWORD", "change-me"),
        ("DB_PASSWORD", ""),
        ("BACKEND_CORS_ORIGINS", ["http://localhost:5173"]),
    ],
)
def test_unsafe_production_settings_are_rejected(field, value):
    values = {**PRODUCTION_SETTINGS, field: value}

    with pytest.raises(ValidationError):
        Settings(_env_file=None, **values)
