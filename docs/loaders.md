# Loaders

Loaders resolve dynamic values during configuration resolution.

The bundled loader is `awsSecret`, which fetches a secret from AWS Secrets Manager and returns it as a string.
Missing loader params or an empty secret value raise an error. Loaders are expected
to fail loudly rather than silently producing defaults.

## Example

```json
{
  "secret": {
    "[awsSecret]": {
      "key": "demo",
      "region": "us-west-2"
    }
  }
}
```

## Registering Loaders

Go-style parity is preserved through a loader registry:

```python
from brek import DefaultLoaders, SetLoaders

SetLoaders(DefaultLoaders())
```

You can then add your own loaders on top of the defaults by passing a dictionary of callables to `SetLoaders()`.

## AWS Loader Notes

The `awsSecret` loader is loaded lazily. The base package does not require `boto3`, but invoking the loader does.
If the secret value is missing or empty, `awsSecret` raises instead of returning
an empty string.

## Optional Config

Loaders are not the place to encode optionality. Optional config should be modeled
at the access layer with `optional_path()` / `OptionalPath()`.
Required config should use `require_path()` / `RequirePath()`.
