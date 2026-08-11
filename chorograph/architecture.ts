// CHOROGRAPH-ARCHITECTURE: this repo's own nodes and edges. Python codebase, so the map is
// declared here as free-standing doc comments; each node's prose names the implementing file.
// Included in both the per-repo render and the estate-wide render (unlike anchor.ts).

/**
 * Python port of brek: typed, layered JSON configuration loader with strict `${VAR}`
 * interpolation and pluggable loaders. Published to PyPI as `brek`; Harper Python services
 * call it at deploy/startup to resolve secrets and environment-specific settings before the
 * app boots. Sibling of brek (Node original, stale) and brek-go (Go port). Stdlib core; boto3
 * only required when awsSecret loader is invoked.
 * @module brek-python in:DevEx tech:"Python, PyPI" tags:active
 */

/**
 * CLI entry (`brek load-config`) and library `LoadConfig()`: acquire file lock, load layered
 * JSON sources, merge, resolve env vars and loaders, atomically write `config/config.json`.
 * src/brek/config.py (`_load_config_locked`, `run`).
 * @fn load-config of:brek-python
 * @calls load-conf-from-files discovers which overlay files apply for this process
 * @calls merge-confs deep-merges layers so later overlays win without clobbering loaders
 * @calls resolve-conf substitutes `${VAR}` and invokes registered loaders
 */

/**
 * Layered JSON file discovery driven by ENVIRONMENT/NODE_ENV, DEPLOYMENT, USER, and BREK/OVERRIDE.
 * src/brek/merge.py (`load_conf_from_files`). Reads `config/default.json` (required base) plus
 * optional `config/environments/{env}.json`, `config/deployments/{dep}.json`,
 * `config/users/{user}.json`.
 * @fn load-conf-from-files of:brek-python
 */

/**
 * Deep-merge of config dicts: shallow keys from later layers override earlier ones; nested dicts
 * recurse unless either side is a loader marker (`[loaderName]`). src/brek/merge.py
 * (`merge_confs`).
 * @fn merge-confs of:brek-python
 */

/**
 * Strict resolution pass over the merged tree: `${VAR}` strings become `os.getenv` lookups
 * (raises `InvalidConf` if unset/empty); `[loaderName]` dicts dispatch to the loader registry.
 * src/brek/resolve.py (`resolve_conf`).
 * @fn resolve-conf of:brek-python
 * @calls awsSecret-loader when config nodes use `[awsSecret]` markers
 */

/**
 * Bundled loader: lazy-imports boto3, calls `secretsmanager:GetSecretValue`, returns the secret
 * string (or base64-encoded binary). Raises on missing params or empty secret — no silent
 * defaults. src/brek/loaders/awssecret.py.
 * @fn awsSecret-loader of:brek-python
 * @calls AWS-Secrets-Manager fetches credentials referenced in JSON config at resolve time
 */

/**
 * Process-wide config accessor with in-memory cache: returns cached dict if loaded; else reads
 * existing `config/config.json` from disk; else falls back to full `load-config` resolution.
 * Thread-safe via `RLock` + `fcntl` file lock on writes. src/brek/config.py (`get_config`).
 * @fn get-config of:brek-python
 * @calls load-config cold-starts resolution when no on-disk cache exists
 */

/**
 * Strict dotted-path accessor for required config — raises `ConfigPathNotFound` if any segment
 * is missing. Preferred over `.get()` for values the service cannot start without.
 * src/brek/access.py (`require_path`).
 * @fn require-path of:brek-python
 */

/**
 * Optional dotted-path accessor with explicit default for genuinely optional branches (e.g.
 * feature-flag tokens). src/brek/access.py (`optional_path`).
 * @fn optional-path of:brek-python
 */
