#!/usr/bin/env python3
# pyre-strict

from importlib import import_module
from typing import Any


# pyre-ignore
def get_class(class_path: str) -> Any:
    module_name, class_name = class_path.rsplit(".", 1)
    module = import_module(module_name)

    return getattr(module, class_name)
