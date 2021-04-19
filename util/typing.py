#!/usr/bin/env python3
# pyre-strict

from typing import Type, TypeVar


T = TypeVar("T")
V = TypeVar("V")


# pyre-fixme[34]: `T` isn't present in the function's parameters.
def checked_cast(typ: Type[V], val: V) -> T:
    if not isinstance(val, typ):
        raise ValueError(f"Value was not of type {type!r}:\n{val!r}")
    # pyre-fixme[7]: Expected `T` but got `V`.
    return val
