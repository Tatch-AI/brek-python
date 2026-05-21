from __future__ import annotations

from .loader import LoaderDict
from .loaders.awssecret import Loader as aws_secret_loader


def default_loaders() -> LoaderDict:
    return {"awsSecret": aws_secret_loader}


DefaultLoaders = default_loaders
