from __future__ import annotations

import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any, TypeVar

from setuptools import build_meta as _orig
from setuptools.build_meta import *  # noqa: F403
from setuptools.dist import Distribution

R = TypeVar("R")


def _generate(fn: Callable[..., R]) -> Callable[..., R]:
    def _wrapped(*args: Any, **kwargs: Any) -> R:
        repo_root = Path(__file__).resolve().parent
        # Run the ffi_build.py script to generate the CFFI bindings
        subprocess.run(
            [sys.executable, "pywayland/ffi_build.py"], check=True, cwd=repo_root
        )
        # Run the scanner module to generate the protocol files
        subprocess.run(
            [sys.executable, "-m", "pywayland.scanner", "--with-protocols"],
            check=True,
            cwd=repo_root,
        )
        Distribution.has_ext_modules = lambda self: True
        return fn(*args, **kwargs)

    return _wrapped


build_wheel = _generate(_orig.build_wheel)
build_sdist = _generate(_orig.build_sdist)
build_editable = _generate(_orig.build_editable)
