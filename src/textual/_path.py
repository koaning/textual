from __future__ import annotations

import inspect
import sys
from pathlib import Path, PurePath


def _make_path_object_relative(path: str | PurePath, obj: object) -> Path:
    """Convert the supplied path to a Path object that is relative to a given Python object.
    If the supplied path is absolute, it will simply be converted to a Path object.
    Used, for example, to return the path of a CSS file relative to a Textual App instance.

    Args:
        path (str | Path): A path.
        obj (object): A Python object to resolve the path relative to.

    Returns:
        Path: A resolved Path object, relative to obj
    """
    path = Path(path)

    # If the path supplied by the user is absolute, we can use it directly
    if path.is_absolute():
        return path

    # Otherwise (relative path), resolve it relative to obj...
    subclass_module = sys.modules[obj.__module__]
    subclass_path = Path(inspect.getfile(subclass_module))
    resolved_path = (subclass_path.parent / path).resolve()
    return resolved_path
