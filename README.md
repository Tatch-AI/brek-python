# brek

[![build status](https://github.com/Tatch-AI/brek-python/actions/workflows/release.yml/badge.svg)](https://github.com/Tatch-AI/brek-python/actions)
[![SemVer](https://img.shields.io/badge/SemVer-2.0.0-blue)]()
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg)](https://conventionalcommits.org)
[![AutoRel](https://img.shields.io/badge/%F0%9F%9A%80%20AutoRel-2D4DDE)](https://github.com/mhweiner/autorel)

This project is the Python port of the original [`brek`](https://github.com/mhweiner/brek) project.

`brek` keeps the same core principles:
- declarative JSON configuration
- layered config files
- environment variable interpolation
- loader-based dynamic values
- a bundled AWS Secrets Manager loader

`brek` stands for **B**locking **R**esolution of **E**nvironment **K**eys.

## Quick Start

Install from PyPI:

```bash
python -m pip install brek
```

Or install from a checkout:

```bash
python -m pip install -e .
```

Create a `config/default.json` file:

```json
{
  "port": 3000,
  "postgres": {
    "host": "localhost"
  },
  "secret": {
    "[awsSecret]": {
      "key": "demo",
      "region": "us-west-2"
    }
  }
}
```

Generate the resolved cache:

```bash
brek load-config
```

Or use it from Python:

```python
from brek import DefaultLoaders, GetConfig, SetLoaders

SetLoaders(DefaultLoaders())
conf = GetConfig()
print(conf["port"])
```

## Features

- JSON config files with default, environment, deployment, and user overlays.
- CLI and environment overrides through `BREK` or `OVERRIDE`.
- Environment variable expansion via `${VAR}` syntax.
- Loader support for runtime values.
- Bundled `awsSecret` loader for AWS Secrets Manager.
- Standard-library core with no mandatory runtime dependencies.

## Docs

- [Getting Started](docs/gettingStarted.md)
- [Loaders](docs/loaders.md)

## Development

```bash
make test
```

## Release

Releases are created by AutoRel from conventional commits on `main` and `next`.
When GitHub creates a release, the `pypi-publish.yml` workflow builds an sdist and wheel
and publishes them to PyPI using Trusted Publishing.

To enable publishing, configure `Tatch-AI/brek-python` as a trusted publisher in the
PyPI project settings for the `pypi` environment and `.github/workflows/pypi-publish.yml`.

## Support

The original implementation lives at [`mhweiner/brek`](https://github.com/mhweiner/brek).

Releases are automated with [autorel](https://github.com/mhweiner/autorel) from conventional commits on `main` and `next`.

Release commits should follow the same conventional-commit format used by the original project.
