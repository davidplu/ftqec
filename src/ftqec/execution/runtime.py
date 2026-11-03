"""Runtime identities for reproducible task caching."""
import sys
from importlib.metadata import version,PackageNotFoundError


def runtime_identity():
    packages={}
    for name in ("stim","numpy","psutil","pymatching","scipy","networkx"):
        try:packages[name]=version(name)
        except PackageNotFoundError:packages[name]=None
    return dict(python=list(sys.version_info[:3]),implementation=sys.implementation.name,packages=packages)
