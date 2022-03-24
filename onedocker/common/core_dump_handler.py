#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

import abc
from typing import Optional


class CoreDumpHandler(abc.ABC):
    @abc.abstractmethod
    def locate_core_dump_file(self) -> Optional[str]:
        """Find the absolute path of the core dump file
        return None if not found.
        """
        pass

    @abc.abstractmethod
    def upload_core_dump_file(self, core_dump_file_path: str, upload_dest: str) -> None:
        """Upload the core dump file to the specified location.
        Keyword arguments:
        core_dump_file_path: absolute path of the generated core dump file
        upload_dest: path to the cloud storage. e.g AWS S3 bucket
        """
        pass
