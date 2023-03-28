# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

import abc


class InsightsService(abc.ABC):
    @abc.abstractmethod
    async def emit_async(self, message: str) -> None:
        pass

    @abc.abstractmethod
    def emit(self, message: str) -> None:
        pass
