# Getting Started

`brek` keeps configuration in JSON files, resolves it into a Python dictionary, and writes the resolved result back to disk for reuse.

## Install

Install from a checkout:

```bash
python -m pip install -e .
```

## Create Config Files

Create a `config` directory in the root of your project. Only `default.json` is required.

```text
root/
└── config/
    ├── deployments/
    ├── environments/
    ├── users/
    └── default.json
```

Example `default.json`:

```json
{
  "port": 3000,
  "postgres": {
    "host": "localhost",
    "password": "pgpassword"
  }
}
```

## Generate the Config Cache

Run:

```bash
brek load-config
```

That resolves the layered config and writes `config/config.json` by default.
Running it again re-resolves and rewrites the cache.

## Read Config in Python

```python
from brek import GetConfig, OptionalPath, RequirePath

conf = GetConfig()
print(RequirePath(conf, "port"))
print(OptionalPath(conf, "observability.logfire.token"))
```

Use `RequirePath` / `require_path()` for values that must exist.
Use `OptionalPath` / `optional_path()` only when a branch is genuinely optional.
Avoid `.get(key, {})` for required config paths.

## Register Loaders

Start with the bundled set:

```python
from brek import DefaultLoaders, SetLoaders

SetLoaders(DefaultLoaders())
```

You can add your own loaders on top of that map before calling `LoadConfig()`.
Loaders should fail loudly when their inputs are incomplete. Missing secrets or
missing loader params should not resolve to empty placeholders.

## CLI

Run the CLI directly:

```bash
brek load-config
```

The import path is `brek` after installation, and `python -m brek load-config` works too.

## Resolution Model

- `LoadConfig()` always re-resolves the JSON config tree and rewrites the generated cache.
- `GetConfig()` returns the in-process cached config if it exists.
- If the cache file exists on disk, `GetConfig()` reads that file instead of re-resolving.
- If neither cache exists, `GetConfig()` falls back to `LoadConfig()`.
