# Business Context — brek-python

> Part of the Harper estate documentation pass (2026-08). Written for the platform rewrite:
> what this library means to the brokerage, not just how it works. Technical detail lives in
> [ARCHITECTURE.md](./ARCHITECTURE.md); the live map renders with `npx chorograph render .`.

## Where this sits in the brokerage

Harper is a commercial insurance brokerage: revenue is **commission on placed premium**. Nothing
in the funnel runs without correctly configured services — database URLs, API keys, carrier
credentials, feature flags, and environment-specific endpoints must be resolved before intake,
quoting, binding, or payments code can execute.

**brek-python does not touch insurance domain data.** It is a **DevEx library** — the Python
port of the original `brek` typed config loader (sibling repos: `brek` Node original, now stale;
`brek-go` Go port). Harper Python services depend on it at **boot time** to:

- Load layered JSON config (`default` → `environment` → `deployment` → `user` → CLI/env overrides).
- Interpolate `${ENV_VAR}` placeholders strictly (missing vars fail loudly, not silently).
- Resolve dynamic values via pluggable **loaders** (bundled: `awsSecret` for AWS Secrets Manager).
- Write a resolved `config/config.json` cache and serve it through `GetConfig()` for the process lifetime.

In brokerage terms: this is **infrastructure glue**, not a funnel stage. It keeps Python
services honest about required configuration so a mis-deployed intake agent, quoting worker, or
payments adapter fails fast at startup rather than mid-call with a null database password.

## Who and what depends on it

- **Harper Python services and libraries** — any deployable that installs `brek` from PyPI and
  ships a `config/` directory (pattern established by the Node `brek` ecosystem).
- **Platform / DevEx** — release automation via AutoRel (`main`/`next` conventional commits →
  GitHub release → `pypi-publish.yml` Trusted Publishing).
- **Humans** — engineers authoring `config/default.json` and environment overlays; ops setting
  `ENVIRONMENT`, `DEPLOYMENT`, `BREK`/`OVERRIDE` at deploy time.

No upstream Harper service calls brek-python over the network — it is imported in-process.

## Domain concepts owned here

| Concept | Meaning |
|---|---|
| Config layer | One JSON file in the merge stack (`default`, `environment`, `deployment`, `user`, overrides) |
| Loader marker | A dict with a single `[loaderName]` key whose value is loader-specific params |
| `${VAR}` interpolation | Strict env-var substitution; unset or empty vars raise `InvalidConf` |
| `config.json` cache | Atomically written resolved config on disk; `GetConfig()` prefers it over re-resolution |
| `require_path` / `optional_path` | Typed accessors — required paths fail with `ConfigPathNotFound`, optional paths return defaults |
| `awsSecret` loader | Fetches a secret string from AWS Secrets Manager at resolve time (requires boto3) |

## Operational status (2026-07 estate forensics)

**Active.** Under active Tatch-AI ownership with AutoRel releases (tags through v0.1.4), PR
checks on unittest, and PyPI publish workflow. Tier-3 estate doc pass (no chorograph CI gate).
Python port parity with the Node `brek` loader model; the original `mhweiner/brek` repo is the
upstream reference implementation.

## Rewrite notes — what must survive

1. **Strict resolution semantics** — missing env vars and missing loader params must continue to
   raise, not default to empty strings. This is the core contract Harper services rely on.
2. **Layered merge order** — `default` < `environment` < `deployment` < `user` < `BREK`/`OVERRIDE`;
   deep merge must not clobber loader markers.
3. **Loader registry** — `SetLoaders(DefaultLoaders())` + custom loaders; `awsSecret` must remain
   bundled for AWS-deployed Python services.
4. **Cache model** — `LoadConfig()` always re-resolves; `GetConfig()` caches in-process and reads
   `config.json` when present. File locking (`fcntl`) prevents concurrent write corruption.
5. **Sibling naming** — estate chorograph maps must keep `brek-python`, `brek`, and `brek-go` as
   distinct module nodes under DevEx; do not collapse them.

## Overlap with siblings

| Repo | Status | Notes |
|---|---|---|
| `brek` (Node) | stale | Original typed config loader; brek-python is a port, not a wrapper |
| `brek-go` | active (parallel doc) | Go port; same layering/loader model, different runtime |
