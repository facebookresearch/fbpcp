#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

import abc


class KeyManagmentService(abc.ABC):
    @abc.abstractmethod
    def sign(self, message: str) -> str:
        pass

    @abc.abstractmethod
    def encrypt(self, plaintext: str) -> str:
        pass
