"""Hatch plugin hooks for registering the dotenv environment collector."""

from __future__ import annotations

from hatchling.plugin import hookimpl

from hatch_dotenv.hooks import DotenvCollector


@hookimpl
def hatch_register_environment_collector() -> type[DotenvCollector]:
    """Register the DotenvCollector plugin with Hatch.

    Returns:
        The DotenvCollector class for use as a Hatch environment collector.
    """
    return DotenvCollector
