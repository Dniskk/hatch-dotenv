# hatch-dotenv

[![PyPI - Version](https://img.shields.io/pypi/v/hatch-dotenv.svg)](https://pypi.org/project/hatch-dotenv)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/hatch-dotenv.svg)](https://pypi.org/project/hatch-dotenv)

A [Hatch](https://hatch.pypa.io/) plugin that loads environment variables from `.env` files.

## Installation

```console
pip install hatch-dotenv
```

## Usage

Add `hatch-dotenv` to your environment requirements and specify `env-files`:

```toml
[tool.hatch.env]
requires = ["hatch-dotenv"]

[tool.hatch.envs.default]
env-files = [".env", ".env.local"]

[tool.hatch.envs.dev]
env-files = [".env", ".env.local", ".env.development"]

[tool.hatch.envs.production]
env-files = [".env", ".env.production"]
```

Works with any environment type:

```toml
[tool.hatch.env]
requires = ["hatch-dotenv", "hatch-pip-compile"]

[tool.hatch.envs.locked]
type = "pip-compile"
env-files = [".env", ".env.local"]
```

## Behavior

- Files are loaded in order; later files override earlier ones
- Missing files emit a warning but don't cause failures
- Variables from `.env` files override existing `env-vars` in config

## License

`hatch-dotenv` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
