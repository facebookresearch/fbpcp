#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict


from shlex import quote


def build_cmd_args(
    **kwargs: object,
) -> str:
    return " ".join(
        [
            f"--{key}={quote(str(value))}"
            for key, value in kwargs.items()
            if value is not None
        ]
    )
