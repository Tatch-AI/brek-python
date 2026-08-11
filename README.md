# brek

> **Orientation**: [docs/BUSINESS_CONTEXT.md](docs/BUSINESS_CONTEXT.md) explains what this
> library means to Harper (DevEx config loader for Python services at boot time) and what must
> survive a rewrite. [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) is the deep technical map.
> The architecture is annotated with [chorograph](https://github.com/flancast90/chorograph)
> — render the live map with `npx chorograph render . --no-open` (declarations live in
> `chorograph/`).

[![build status](https://github.com/Tatch-AI/brek-python/actions/workflows/release.yml/badge.svg)](https://github.com/Tatch-AI/brek-python/actions)
[![SemVer](https://img.shields.io/badge/SemVer-2.0.0-blue)]()
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg)](https://conventionalcommits.org)
[![AutoRel](https://img.shields.io/badge/%F0%9F%9A%80%20AutoRel-2D4DDE)](https://github.com/mhweiner/autorel)

This project is the Python port of the original [`brek`](https://github.com/mhweiner/brek) project.

`brek` keeps the same core principles:
- declarative JSON configuration
- layered config files
- strict environment variable interpolation via `${VAR}`
- loader-based dynamic values
- a bundled AWS Secrets Manager loader
- strict runtime resolution for required config paths

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

`brek load-config` always re-resolves config and rewrites the generated cache file.
Within a running Python process, `GetConfig()` is cached after the first load.

Or use it from Python:

```python
from brek import DefaultLoaders, GetConfig, SetLoaders, require_path

SetLoaders(DefaultLoaders())
conf = GetConfig()
print(require_path(conf, "port"))
```

## Features

- JSON config files with default, environment, deployment, and user overlays.
- CLI and environment overrides through `BREK` or `OVERRIDE`.
- Environment variable expansion via `${VAR}` syntax.
- Loader support for runtime values.
- Bundled `awsSecret` loader for AWS Secrets Manager.
- Strict access helpers for required and optional paths.
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
