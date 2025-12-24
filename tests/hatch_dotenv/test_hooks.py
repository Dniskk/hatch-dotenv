"""Tests for hatch_dotenv.hooks module."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from unittest.mock import MagicMock

import pytest

from hatch_dotenv.hooks import DotenvCollector, assert_config

if TYPE_CHECKING:
    from pathlib import Path


class TestAssertConfig:
    """Tests for assert_config function."""

    def test_valid_empty_config(self) -> None:
        """Empty config should pass validation."""
        assert_config({})

    def test_valid_config_with_env_files(self) -> None:
        """Config with valid env-files list should pass."""
        config: dict[str, Any] = {
            "default": {"env-files": [".env", ".env.local"]},
        }
        assert_config(config)

    def test_valid_config_with_fail_on_missing(self) -> None:
        """Config with valid fail-on-missing bool should pass."""
        config: dict[str, Any] = {
            "default": {"fail-on-missing": True},
        }
        assert_config(config)

    def test_valid_config_with_both_options(self) -> None:
        """Config with both options should pass."""
        config: dict[str, Any] = {
            "default": {"env-files": [".env"], "fail-on-missing": False},
        }
        assert_config(config)

    def test_invalid_key_type(self) -> None:
        """Non-string keys should raise TypeError."""
        config: dict[Any, Any] = {123: {"env-files": []}}
        with pytest.raises(TypeError, match="config keys must be strings"):
            assert_config(config)

    def test_invalid_env_files_type(self) -> None:
        """Non-list env-files should raise TypeError."""
        config: dict[str, Any] = {"default": {"env-files": ".env"}}
        with pytest.raises(TypeError, match="env-files must be a list"):
            assert_config(config)

    def test_invalid_fail_on_missing_type(self) -> None:
        """Non-bool fail-on-missing should raise TypeError."""
        config: dict[str, Any] = {"default": {"fail-on-missing": "yes"}}
        with pytest.raises(TypeError, match="fail-on-missing must be a bool"):
            assert_config(config)


class TestDotenvCollector:
    """Tests for DotenvCollector class."""

    @pytest.fixture
    def mock_collector(self, tmp_path: Path) -> MagicMock:
        """Create a mock DotenvCollector for testing."""
        collector = MagicMock(spec=DotenvCollector)
        collector.root = tmp_path
        collector.config = {}
        return collector

    def test_plugin_name(self) -> None:
        """Plugin name should be correct."""
        assert DotenvCollector.PLUGIN_NAME == "dotenv"

    def test_get_initial_config_returns_empty(self) -> None:
        """get_initial_config should return empty dict."""
        collector = MagicMock(spec=DotenvCollector)
        result = DotenvCollector.get_initial_config(collector)
        assert result == {}


class TestFinalizeConfig:
    """Tests for DotenvCollector.finalize_config method."""

    @pytest.fixture
    def mock_collector(self, tmp_path: Path) -> MagicMock:
        """Create a mock DotenvCollector for testing finalize_config."""
        collector = MagicMock(spec=DotenvCollector)
        collector.root = tmp_path
        collector.config = {}
        return collector

    def _finalize(self, collector: MagicMock, config: dict[str, dict[str, Any]]) -> None:
        """Helper to call finalize_config with the mock collector."""
        DotenvCollector.finalize_config(collector, config)

    def test_empty_config(self, mock_collector: MagicMock) -> None:
        """Empty config should be unchanged."""
        config: dict[str, dict[str, Any]] = {}
        self._finalize(mock_collector, config)
        assert config == {}

    def test_no_collector_config(self, mock_collector: MagicMock) -> None:
        """Environment without collector config should be unchanged."""
        config: dict[str, dict[str, Any]] = {
            "default": {"type": "virtual"},
        }
        self._finalize(mock_collector, config)
        assert config == {"default": {"type": "virtual"}}

    def test_empty_env_files_list(self, mock_collector: MagicMock) -> None:
        """Empty env-files list should not add env-vars."""
        mock_collector.config = {"default": {"env-files": []}}
        config: dict[str, dict[str, Any]] = {"default": {}}
        self._finalize(mock_collector, config)
        assert "env-vars" not in config["default"]

    def test_load_single_env_file(self, mock_collector: MagicMock) -> None:
        """Loading a single .env file should populate env-vars."""
        env_file = mock_collector.root / ".env"
        env_file.write_text("TEST_VAR=test_value\nANOTHER_VAR=another_value\n")

        mock_collector.config = {"default": {"env-files": [".env"]}}
        config: dict[str, dict[str, Any]] = {"default": {}}

        self._finalize(mock_collector, config)

        assert config["default"]["env-vars"]["TEST_VAR"] == "test_value"
        assert config["default"]["env-vars"]["ANOTHER_VAR"] == "another_value"

    def test_load_multiple_env_files_with_precedence(self, mock_collector: MagicMock) -> None:
        """Later .env files should override earlier ones."""
        env_file1 = mock_collector.root / ".env"
        env_file1.write_text("SHARED_VAR=first_value\nFIRST_ONLY=first\n")

        env_file2 = mock_collector.root / ".env.local"
        env_file2.write_text("SHARED_VAR=second_value\nSECOND_ONLY=second\n")

        mock_collector.config = {"default": {"env-files": [".env", ".env.local"]}}
        config: dict[str, dict[str, Any]] = {"default": {}}

        self._finalize(mock_collector, config)

        assert config["default"]["env-vars"]["SHARED_VAR"] == "second_value"
        assert config["default"]["env-vars"]["FIRST_ONLY"] == "first"
        assert config["default"]["env-vars"]["SECOND_ONLY"] == "second"

    def test_missing_file_silently_skipped_by_default(self, mock_collector: MagicMock) -> None:
        """Missing files should be skipped when fail-on-missing is False."""
        mock_collector.config = {"default": {"env-files": [".env.nonexistent"]}}
        config: dict[str, dict[str, Any]] = {"default": {}}

        self._finalize(mock_collector, config)

        # env-vars dict is created but empty since no files were loaded
        assert config["default"]["env-vars"] == {}

    def test_missing_file_raises_when_fail_on_missing(self, mock_collector: MagicMock) -> None:
        """Missing files should raise FileNotFoundError when fail-on-missing is True."""
        mock_collector.config = {
            "default": {"env-files": [".env.nonexistent"], "fail-on-missing": True},
        }
        config: dict[str, dict[str, Any]] = {"default": {}}

        with pytest.raises(FileNotFoundError, match="Environment file not found"):
            self._finalize(mock_collector, config)

    def test_partial_missing_files_without_fail(self, mock_collector: MagicMock) -> None:
        """Existing files should be loaded even when some are missing."""
        env_file = mock_collector.root / ".env"
        env_file.write_text("EXISTING_VAR=exists\n")

        mock_collector.config = {"default": {"env-files": [".env", ".env.missing"]}}
        config: dict[str, dict[str, Any]] = {"default": {}}

        self._finalize(mock_collector, config)

        assert config["default"]["env-vars"]["EXISTING_VAR"] == "exists"

    def test_preserves_existing_env_vars(self, mock_collector: MagicMock) -> None:
        """Existing env-vars should be preserved and extended."""
        env_file = mock_collector.root / ".env"
        env_file.write_text("NEW_VAR=new_value\n")

        mock_collector.config = {"default": {"env-files": [".env"]}}
        config: dict[str, dict[str, Any]] = {
            "default": {"env-vars": {"EXISTING_VAR": "existing_value"}},
        }

        self._finalize(mock_collector, config)

        assert config["default"]["env-vars"]["EXISTING_VAR"] == "existing_value"
        assert config["default"]["env-vars"]["NEW_VAR"] == "new_value"

    def test_dotenv_overrides_existing_env_vars(self, mock_collector: MagicMock) -> None:
        """.env file values should override existing env-vars."""
        env_file = mock_collector.root / ".env"
        env_file.write_text("OVERRIDE_VAR=overridden_value\n")

        mock_collector.config = {"default": {"env-files": [".env"]}}
        config: dict[str, dict[str, Any]] = {
            "default": {"env-vars": {"OVERRIDE_VAR": "original_value"}},
        }

        self._finalize(mock_collector, config)

        assert config["default"]["env-vars"]["OVERRIDE_VAR"] == "overridden_value"

    def test_multiple_environments(self, mock_collector: MagicMock) -> None:
        """Multiple environments should be handled independently."""
        env_file = mock_collector.root / ".env"
        env_file.write_text("SHARED=shared\n")

        dev_env_file = mock_collector.root / ".env.dev"
        dev_env_file.write_text("DEV_VAR=dev_value\n")

        mock_collector.config = {
            "default": {"env-files": [".env"]},
            "dev": {"env-files": [".env", ".env.dev"]},
        }
        config: dict[str, dict[str, Any]] = {
            "default": {},
            "dev": {"type": "pip-compile"},
            "prod": {},
        }

        self._finalize(mock_collector, config)

        assert config["default"]["env-vars"]["SHARED"] == "shared"
        assert "DEV_VAR" not in config["default"].get("env-vars", {})

        assert config["dev"]["env-vars"]["SHARED"] == "shared"
        assert config["dev"]["env-vars"]["DEV_VAR"] == "dev_value"
        assert config["dev"]["type"] == "pip-compile"

        assert "env-vars" not in config["prod"]

    def test_works_with_any_environment_type(self, mock_collector: MagicMock) -> None:
        """Collector should work with any environment type."""
        env_file = mock_collector.root / ".env"
        env_file.write_text("MY_VAR=my_value\n")

        mock_collector.config = {
            "virtual_env": {"env-files": [".env"]},
            "pip_compile_env": {"env-files": [".env"]},
            "custom_env": {"env-files": [".env"]},
        }
        config: dict[str, dict[str, Any]] = {
            "virtual_env": {"type": "virtual"},
            "pip_compile_env": {"type": "pip-compile"},
            "custom_env": {"type": "some-custom-type"},
        }

        self._finalize(mock_collector, config)

        for env_name in ["virtual_env", "pip_compile_env", "custom_env"]:
            assert config[env_name]["env-vars"]["MY_VAR"] == "my_value"

    def test_filters_none_values(self, mock_collector: MagicMock) -> None:
        """None values from dotenv should be filtered out."""
        env_file = mock_collector.root / ".env"
        env_file.write_text("VALID_VAR=value\nEMPTY_VAR=\n")

        mock_collector.config = {"default": {"env-files": [".env"]}}
        config: dict[str, dict[str, Any]] = {"default": {}}

        self._finalize(mock_collector, config)

        assert config["default"]["env-vars"]["VALID_VAR"] == "value"
        # Empty string values are kept (only None is filtered)
        assert not config["default"]["env-vars"]["EMPTY_VAR"]

    def test_subdirectory_env_file(self, mock_collector: MagicMock) -> None:
        """Should load .env files from subdirectories."""
        subdir = mock_collector.root / "config"
        subdir.mkdir()
        env_file = subdir / ".env"
        env_file.write_text("SUBDIR_VAR=subdir_value\n")

        mock_collector.config = {"default": {"env-files": ["config/.env"]}}
        config: dict[str, dict[str, Any]] = {"default": {}}

        self._finalize(mock_collector, config)

        assert config["default"]["env-vars"]["SUBDIR_VAR"] == "subdir_value"

    def test_env_without_collector_config_but_in_main_config(self, mock_collector: MagicMock) -> None:
        """Env defined in config but not in collector.config should be unchanged."""
        mock_collector.config = {"other": {"env-files": [".env"]}}
        config: dict[str, dict[str, Any]] = {
            "default": {"type": "virtual"},
        }

        self._finalize(mock_collector, config)

        assert config["default"] == {"type": "virtual"}
