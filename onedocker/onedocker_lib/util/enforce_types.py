#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
# File derived from https://github.com/matchawine/python-enforce-typing/
# TODO: Import this Enforce Types library to fbcode

import inspect
import typing
from contextlib import suppress
from functools import wraps

from fbpcs.error.owdl import OWDLParsingError


def enforce_types(callable):
    spec = inspect.getfullargspec(callable)

    def check_types(*args, **kwargs):
        parameters = dict(zip(spec.args, args))
        parameters.update(kwargs)
        for name, value in parameters.items():
            with suppress(KeyError):  # Assume un-annotated parameters can be any type
                type_hint = spec.annotations[name]
                if isinstance(type_hint, typing._SpecialForm):
                    # No check for typing.Any, typing.Union, typing.ClassVar (without parameters)
                    continue
                try:
                    actual_type = type_hint.__origin__
                except AttributeError:
                    # In case of non-typing types (such as <class 'int'>, for instance)
                    actual_type = type_hint
                # In Python 3.8 one would replace the try/except with
                # actual_type = typing.get_origin(type_hint) or type_hint
                if isinstance(actual_type, typing._SpecialForm):
                    # case of typing.Union[…] or typing.ClassVar[…]
                    actual_type = type_hint.__args__

                if not isinstance(value, actual_type):
                    raise OWDLParsingError(
                        f"Unexpected type for '{name}' (expected {type_hint} but found {type(value)})"
                    )

    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            check_types(*args, **kwargs)
            return func(*args, **kwargs)

        return wrapper

    if inspect.isclass(callable):
        callable.__init__ = decorate(callable.__init__)
        return callable

    return decorate(callable)
