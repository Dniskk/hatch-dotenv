# hatch-dotenv

[![PyPI - Version](https://img.shields.io/pypi/v/hatch-dotenv.svg)](https://pypi.org/project/hatch-dotenv)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/hatch-dotenv.svg)](https://pypi.org/project/hatch-dotenv)

A [Hatch](https://hatch.pypa.io/) plugin that loads environment variables from `.env` files.

## Installation

```console
pip install hatch-dotenv
```

## Usage

Add `hatch-dotenv` to your environment requirements and configure the collector for each environment:

```toml
[tool.hatch.env]
requires = ["hatch-dotenv"]

# Configure env-files for the default environment
[tool.hatch.env.collectors.dotenv.default]
env-files = [".env", ".env.local"]

# Configure env-files for other environments
[tool.hatch.env.collectors.dotenv.dev]
env-files = [".env", ".env.local", ".env.development"]

[tool.hatch.env.collectors.dotenv.production]
env-files = [".env", ".env.production"]
```

Works with any environment type:

```toml
[tool.hatch.env]
requires = ["hatch-dotenv", "hatch-pip-compile"]

[tool.hatch.envs.locked]
type = "pip-compile"

[tool.hatch.env.collectors.dotenv.locked]
env-files = [".env", ".env.local"]
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `env-files` | list[str] | `[]` | List of `.env` file paths to load |
| `fail-on-missing` | bool | `false` | Raise an error if a file is missing |

### Strict mode

To fail when an env file is missing, set `fail-on-missing = true`:

```toml
[tool.hatch.env.collectors.dotenv.default]
env-files = [".env"]
fail-on-missing = true
```

## Behavior

- Files are loaded in order; later files override earlier ones
- Missing files are silently skipped (unless `fail-on-missing = true`)
- Variables from `.env` files override existing `env-vars` in config

## License

`hatch-dotenv` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
