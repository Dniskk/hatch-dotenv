"""Hatch environment collector plugin that loads environment variables from .env files."""

from __future__ import annotations

import shlex
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar, NotRequired, TypedDict, cast

from dotenv import dotenv_values
from hatch.env.collectors.plugin.interface import EnvironmentCollectorInterface
from typing_extensions import override

if TYPE_CHECKING:
    from typing import Any


CollectorConfig = TypedDict(
    "CollectorConfig", {"env-files": NotRequired[list[str]], "fail-on_missing": NotRequired[bool]}, total=False
)


def assert_config(config: dict[Any, Any]) -> None:
    """Check if the config is a valid dict.

    Args:
        config: The config to check.

    Raises:
        TypeError: If the config is not a valid dict.
            If the config keys are not strings.
            If the config values are not valid CollectorConfig.
            If the env_files are not a list.
            If the fail_on_missing are not a bool.
    """
    if any(not isinstance(k, str) for k in config):
        error_message = f"config keys must be strings, got {list(config.keys())}"
        raise TypeError(error_message)
    for v in config.values():
        if "env-files" in v and not isinstance(v["env-files"], list):
            error_message = f"env-files must be a list, got {type(v['env-files'])}"
            raise TypeError(error_message)
        if "fail-on-missing" in v and not isinstance(v["fail-on-missing"], bool):
            error_message = f"fail-on-missing must be a bool, got {type(v['fail-on-missing'])}"
            raise TypeError(error_message)


class DotenvCollector(EnvironmentCollectorInterface):
    """An environment collector that loads .env files into environment variables.

    This collector reads `env-files` from each environment's configuration and
    merges the loaded variables into the environment's `env-vars` setting.
    This works with any environment type (virtual, pip-compile, etc.).

    Configuration:
        env-files: A list of .env file paths to load. Files are loaded in order,
                   with later files overriding earlier ones. Missing files emit
                   warnings but do not cause failures.

    Example:
        ```toml
        [tool.hatch.env]
        requires = ["hatch-dotenv"]

        [tool.hatch.envs.default]
        env-files = [".env", ".env.local"]

        [tool.hatch.envs.dev]
        type = "pip-compile"  # Works with any type!
        env-files = [".env", ".env.development"]
        ```
    """

    PLUGIN_NAME: ClassVar[str] = "dotenv"

    @override
    def get_initial_config(self) -> dict[str, dict[str, Any]]:
        """Return initial environment configurations.

        Returns:
            Empty dict - we don't create new environments, only modify existing ones.
        """
        return {}

    @override
    def finalize_config(self, config: dict[str, dict[str, Any]]) -> None:
        """Modify environment configurations to include .env file variables.

        This method is called after all environment configurations are collected.
        It reads `env-files` from each environment and merges the loaded variables
        into the environment's `env-vars`.

        When `fail-on-missing=true` and a referenced .env file is missing, a
        `pre-install-commands` entry is appended to that env so the failure
        only surfaces when the env is actually prepared — leaving unrelated
        envs (and commands like `hatch publish`) untouched.

        Args:
            config: Dictionary of environment name -> environment configuration.
        """
        assert_config(self.config)  # pyright: ignore [reportUnknownMemberType, reportUnknownArgumentType]
        collector_config = cast("dict[str, CollectorConfig]", self.config)

        for env_name, env_entry in config.items():
            env_config = collector_config.get(env_name, {})
            files = env_config.get("env-files", [])
            fail_on_missing = env_config.get("fail-on-missing", False)
            if not files:
                continue

            env_vars: dict[str, str] = env_entry.setdefault("env-vars", {})

            for env_file in files:
                env_path = Path(self.root) / env_file  # pyright: ignore[reportUnknownArgumentType]
                if not env_path.exists():
                    if fail_on_missing:
                        _inject_missing_file_failure(env_entry, env_name, env_file)
                    continue

                loaded_vars = dotenv_values(env_path)
                env_vars.update({k: v for k, v in loaded_vars.items() if v is not None})


def _inject_missing_file_failure(env_entry: dict[str, Any], env_name: str, env_file: str) -> None:
    """Append a pre-install command that fails with a clear message about the missing file."""
    error_message = f"hatch-dotenv: required env-file not found for env [{env_name}]: {env_file}"
    # shlex.quote keeps the python script intact regardless of the message contents.
    py_code = f"import sys; sys.exit({error_message!r})"
    fail_command = f"python -c {shlex.quote(py_code)}"
    pre_install: list[str] = env_entry.setdefault("pre-install-commands", [])
    if fail_command not in pre_install:
        pre_install.append(fail_command)
