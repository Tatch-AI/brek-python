# AWS Secrets Example

This example shows the bundled `awsSecret` loader in a minimal app.
It also demonstrates the strict config read path: `GetConfig()` returns the
resolved tree, and required paths should be accessed explicitly.

## Run

Install the project first:

```bash
python -m pip install -e .
```

Then generate the config cache:

```bash
brek load-config
```

The example uses `DefaultLoaders()` so the `awsSecret` loader is available before `GetConfig()` runs.
