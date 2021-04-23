#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

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
