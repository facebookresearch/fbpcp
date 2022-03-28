#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

import logging
import os
import uuid
from pathlib import Path
from typing import Optional

from fbpcp.service.storage import StorageService
from onedocker.common.core_dump_handler import CoreDumpHandler

CORE_DUMP_FILE_PREFIX = "core"


class AWSCoreDumpHandler(CoreDumpHandler):
    def __init__(self, storage_svc: StorageService) -> None:
        self.storage_svc = storage_svc
        self.logger: logging.Logger = logging.getLogger("__name__")

    def locate_core_dump_file(self) -> Optional[str]:
        """Find the absolute path of the generated core dump file
        AWS: /proc/sys/kernel/core_pattern: core
        The core dump file will be generated in the current
        working dir. File name starts with 'core'.
        """
        cwd = os.getcwd()
        file_list = [f for f in os.listdir(cwd) if f.startswith(CORE_DUMP_FILE_PREFIX)]

        if len(file_list) == 0:
            self.logger.error(f"Core dump file not found in {cwd}!")
            return None

        # One core file is generated for each run
        file_path = os.path.join(cwd, file_list[0])

        if not Path(file_path).is_file:
            # If the file path points to a non-file type
            # return None
            self.logger.error(f"{file_path} is not a file.")
            return None

        self.logger.info(f"Core dump file locates in {file_path}")
        return file_path

    def upload_core_dump_file(self, core_dump_file_path: str, upload_dest: str) -> None:
        """Upload the core dump file to S3
        Valid upload_dest for AWS is the S3 bucket e.g. http://test.s3.us-west-2.amazonaws.com/
        """
        # uploaded core file named as core.uuid
        file_suffix = str(uuid.uuid4())
        s3_dest = f"{upload_dest}core.{file_suffix}"
        self.storage_svc.copy(core_dump_file_path, s3_dest)
        self.logger.info(f"Core dump file was uploaded to {s3_dest}")
