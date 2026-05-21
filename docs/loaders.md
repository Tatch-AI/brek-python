# Loaders

Loaders resolve dynamic values during configuration resolution.

The bundled loader is `awsSecret`, which fetches a secret from AWS Secrets Manager and returns it as a string.

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
