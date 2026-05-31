"""Модульные тесты для Config"""

import os
from unittest.mock import patch
import pytest
from src.utils.config import Config


class TestConfig:
    def test_default_values(self):
        c = Config()
        assert c.api_base_url == "http://localhost:5000/api"
        assert c.app_name == "🌸 FloraStock"
        assert c.app_version == "1.0.0"
        assert c.window_width == 1200
        assert c.window_height == 800
        assert c.api_timeout == 30

    def test_api_headers(self):
        c = Config()
        headers = c.api_headers
        assert headers["Content-Type"] == "application/json"
        assert headers["Accept"] == "application/json"

    def test_is_development_default(self):
        c = Config()
        assert c.is_development is False

    @patch.dict(os.environ, {"ENVIRONMENT": "development"}, clear=True)
    def test_is_development_true(self):
        c = Config()
        assert c.is_development is True

    @patch.dict(os.environ, {"API_BASE_URL": "http://test:8080/api"}, clear=True)
    def test_env_override(self):
        c = Config()
        assert c.api_base_url == "http://test:8080/api"

    def test_log_level_default(self):
        c = Config()
        assert c.log_level == "INFO"

    def test_create_directories(self):
        c = Config()
        assert c.resources_dir.exists()
