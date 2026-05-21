# Getting Started

`brek-python` keeps configuration in JSON files, resolves it into a Python dictionary at startup, and writes the resolved result back to disk for reuse.

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

## Read Config in Python

```python
from brek import GetConfig

conf = GetConfig()
print(conf["port"])
```

## Register Loaders

Start with the bundled set:

```python
from brek import DefaultLoaders, SetLoaders

SetLoaders(DefaultLoaders())
```

You can add your own loaders on top of that map before calling `LoadConfig()`.

## CLI

Run the CLI directly:

```bash
brek load-config
```

The import path is `brek` after installation, and `python -m brek load-config` works too.
