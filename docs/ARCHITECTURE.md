# Architecture — brek-python

> Evidence-based technical map of the `brek` Python package. Chorograph annotations live in
> `chorograph/`; render with `npx chorograph render . --no-open`.

## Package overview

| Item | Value |
|---|---|
| PyPI name | `brek` |
| Import path | `brek` (`src/brek/`) |
| Python | ≥ 3.11 |
| Runtime deps | None (stdlib); `boto3` optional, required only for `awsSecret` loader |
| Entry console script | `brek` → `brek.cli:main` |

## Entrypoints

| Entry | File | Behavior |
|---|---|---|
| `brek load-config` | `src/brek/cli.py` → `config.run` | Resolves layered config, writes `config/config.json`, exits 0/1 |
| `python -m brek load-config` | `src/brek/__main__.py` | Same as CLI |
| `GetConfig()` / `get_config()` | `src/brek/config.py` | Returns cached or on-disk resolved config; cold-starts via `load_config()` |
| `LoadConfig()` / `load_config()` | `src/brek/config.py` | Always re-resolves and rewrites cache |
| `SetLoaders()` / `set_loaders()` | `src/brek/config.py` | Registers custom loader callables atop defaults |

## Config file layout (consumer repos)

```text
config/
├── default.json              # required base layer
├── environments/{env}.json   # selected by ENVIRONMENT or NODE_ENV
├── deployments/{dep}.json    # selected by DEPLOYMENT
├── users/{user}.json         # selected by USER
├── config.json               # generated resolved cache (gitignored)
└── config.lock               # fcntl lock file for concurrent writes
```

Paths overridable via `BREK_CONFIG_DIR` (read) and `BREK_WRITE_DIR` (write cache).

## Environment variables

| Variable | Used by | Purpose |
|---|---|---|
| `ENVIRONMENT` / `NODE_ENV` | `env.get_env_arguments` | Selects `config/environments/{value}.json` |
| `DEPLOYMENT` | `env.get_env_arguments` | Selects `config/deployments/{value}.json` |
| `USER` | `env.get_env_arguments` | Selects `config/users/{value}.json` |
| `BREK` / `OVERRIDE` | `env.get_env_overrides` | JSON object merged last (CLI-style overrides) |
| `BREK_CONFIG_DIR` | `paths.config_dir` | Config root (default `config`) |
| `BREK_WRITE_DIR` | `paths.write_dir` | Where `config.json` / `config.lock` are written |
| `BREK_DEBUG` | `debug.debug` | Verbose resolution logging when truthy |

Individual `${VAR}` placeholders in JSON resolve against `os.getenv` at resolve time.

## Resolution pipeline

```text
load_config()
  └─ get_env_arguments()          # ENVIRONMENT, DEPLOYMENT, USER, BREK/OVERRIDE
  └─ load_conf_from_files()     # read JSON layers (missing files → {})
  └─ merge_confs()              # deep merge in order
  └─ resolve_conf()             # ${VAR} + [loader] dispatch
  └─ write_conf_json()          # atomic write via tempfile + os.replace
  └─ cache in _cached_config
```

`get_config()` short-circuits: in-memory cache → existing `config.json` on disk → full pipeline.

## Loaders

| Name | Module | Params | External |
|---|---|---|---|
| `awsSecret` | `src/brek/loaders/awssecret.py` | `{ key, region }` | AWS Secrets Manager (`GetSecretValue`) |

Loader markers in JSON look like:

```json
{ "[awsSecret]": { "key": "my/secret", "region": "us-west-2" } }
```

Custom loaders register via `SetLoaders({**DefaultLoaders(), "myLoader": fn})`.

## Access helpers

| Function | Module | On missing path |
|---|---|---|
| `require_path(conf, "a.b.c")` | `src/brek/access.py` | Raises `ConfigPathNotFound` |
| `optional_path(conf, "a.b.c", default=None)` | `src/brek/access.py` | Returns `default` |

## Error types (`src/brek/errors.py`)

| Exception | When |
|---|---|
| `InvalidConf` | Bad JSON, unset `${VAR}`, invalid BREK/OVERRIDE JSON |
| `LoaderNotFound` | `[unknownLoader]` in config |
| `ConfigPathNotFound` | `require_path` traversal fails |
| `ConfNotLoaded` | Reserved; not raised in current code paths |

## Data stores

**None.** This library reads/writes local JSON files only. No databases, caches, queues, or
Kafka topics.

## External services

| Service | Integration | Why |
|---|---|---|
| AWS Secrets Manager | `awsSecret` loader via boto3 | Resolve secret strings referenced in config JSON |
| PyPI | `pypi-publish.yml` Trusted Publishing | Package distribution |

## Key flows

### 1. Deploy-time config bake (`brek load-config`)

Container build or ECS task init runs `brek load-config` with env vars set. Layered JSON is
merged and resolved (including Secrets Manager fetches), producing `config/config.json` baked
into the image or ephemeral volume.

### 2. Runtime config read (`GetConfig()`)

Application imports `brek`, calls `GetConfig()` once at startup. If `config.json` exists from
step 1, reads it without re-fetching secrets. Subsequent calls return the in-process cache.

### 3. Local dev with overrides

Engineer sets `BREK='{"port":4000}'` or `OVERRIDE` to patch config without editing files.
`LoadConfig()` picks up overrides on next explicit reload.

## Testing & CI

| Workflow | Trigger | Action |
|---|---|---|
| `pr-check.yml` | PR to `main` | `python -m unittest discover -s tests` |
| `release.yml` | push `main`/`next` | AutoRel semantic versioning |
| `pypi-publish.yml` | GitHub release created | Build sdist/wheel, publish to PyPI |

Tests live in `tests/test_brek.py` — cover merge, resolve, env overrides, awsSecret mocking,
file locking, and access helpers.

## Deploy story

Library only — consumers pin `brek` in their `pyproject.toml` / `requirements.txt`. This repo
publishes to PyPI on release; no Harper ECS/Lambda deployable of its own.
