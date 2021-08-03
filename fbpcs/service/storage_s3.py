#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

import os
from os import path
from os.path import join, normpath, relpath
from typing import Any, Dict, Optional, List

from fbpcs.entity.file_information import FileInfo
from fbpcs.gateway.s3 import S3Gateway
from fbpcs.service.storage import PathType, StorageService
from fbpcs.util.s3path import S3Path


class S3StorageService(StorageService):
    def __init__(
        self,
        region: str = "us-west-1",
        access_key_id: Optional[str] = None,
        access_key_data: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.s3_gateway = S3Gateway(region, access_key_id, access_key_data, config)

    def read(self, filename: str) -> str:
        """Read a file data
        Keyword arguments:
        filename -- "https://bucket-name.s3.Region.amazonaws.com/key-name"
        """
        s3_path = S3Path(filename)
        return self.s3_gateway.get_object(s3_path.bucket, s3_path.key)

    def write(self, filename: str, data: str) -> None:
        """Write data into a file
        Keyword arguments:
        filename -- "https://bucket-name.s3.Region.amazonaws.com/key-name"`
        """
        s3_path = S3Path(filename)
        self.s3_gateway.put_object(s3_path.bucket, s3_path.key, data)

    def copy(self, source: str, destination: str, recursive: bool = False) -> None:
        """Move a file or folder between local storage and S3, as well as, S3 and S3
        Keyword arguments:
        source -- source file
        destination -- destination file
        recursive -- whether to recursively copy a folder
        """
        if StorageService.path_type(source) == PathType.Local:
            # from local to S3
            if StorageService.path_type(destination) == PathType.Local:
                raise ValueError("Both source and destination are local files")
            s3_path = S3Path(destination)
            if path.isdir(source):
                if not recursive:
                    raise ValueError(f"Source {source} is a folder. Use --recursive")
                self.upload_dir(source, s3_path.bucket, s3_path.key)
            else:
                self.s3_gateway.upload_file(source, s3_path.bucket, s3_path.key)
        else:
            source_s3_path = S3Path(source)
            if StorageService.path_type(destination) == PathType.S3:
                # from S3 to S3
                dest_s3_path = S3Path(destination)
                if source_s3_path == dest_s3_path:
                    raise ValueError(
                        f"Source {source} and destination {destination} are the same"
                    )

                if source.endswith("/"):
                    if not recursive:
                        raise ValueError(
                            f"Source {source} is a folder. Use --recursive"
                        )

                    self.copy_dir(
                        source_s3_path.bucket,
                        source_s3_path.key + "/",
                        dest_s3_path.bucket,
                        dest_s3_path.key,
                    )
                else:
                    self.s3_gateway.copy(
                        source_s3_path.bucket,
                        source_s3_path.key,
                        dest_s3_path.bucket,
                        dest_s3_path.key,
                    )
            else:
                # from S3 to local
                if source.endswith("/"):
                    if not recursive:
                        raise ValueError(
                            f"Source {source} is a folder. Use --recursive"
                        )
                    self.download_dir(
                        source_s3_path.bucket,
                        source_s3_path.key + "/",
                        destination,
                    )
                else:
                    self.s3_gateway.download_file(
                        source_s3_path.bucket, source_s3_path.key, destination
                    )

    def upload_dir(self, source: str, s3_path_bucket: str, s3_path_key: str) -> None:
        for root, dirs, files in os.walk(source):
            for file in files:
                local_path = join(root, file)
                destination_path = s3_path_key + "/" + relpath(local_path, source)

                self.s3_gateway.upload_file(
                    local_path,
                    s3_path_bucket,
                    destination_path,
                )
            for dir in dirs:
                local_path = join(root, dir)
                destination_path = s3_path_key + "/" + relpath(local_path, source)

                self.s3_gateway.put_object(
                    s3_path_bucket,
                    destination_path + "/",
                    "",
                )

    def download_dir(
        self, s3_path_bucket: str, s3_path_key: str, destination: str
    ) -> None:
        if not self.s3_gateway.object_exists(s3_path_bucket, s3_path_key):
            raise ValueError(
                f"Key {s3_path_key} does not exist in bucket {s3_path_bucket}"
            )
        keys = self.s3_gateway.list_object2(s3_path_bucket, s3_path_key)
        for key in keys:
            local_path = normpath(destination + "/" + key[len(s3_path_key) :])
            if key.endswith("/"):
                if not path.exists(local_path):
                    os.makedirs(local_path)
            else:
                self.s3_gateway.download_file(s3_path_bucket, key, local_path)

    def copy_dir(
        self,
        source_bucket: str,
        source_key: str,
        destination_bucket: str,
        destination_key: str,
    ) -> None:
        if not self.s3_gateway.object_exists(source_bucket, source_key):
            raise ValueError(
                f"Key {source_key} does not exist in bucket {source_bucket}"
            )
        keys = self.s3_gateway.list_object2(source_bucket, source_key)
        for key in keys:
            destination_path = destination_key + "/" + key[len(source_key) :]
            if key.endswith("/"):
                self.s3_gateway.put_object(
                    source_bucket,
                    destination_path,
                    "",
                )
            else:
                self.s3_gateway.copy(
                    source_bucket,
                    key,
                    destination_bucket,
                    destination_path,
                )

    def delete(self, filename: str) -> None:
        """Delete an s3 file
        Keyword arguments:
        filename -- the s3 file to be deleted
        """
        if StorageService.path_type(filename) == PathType.S3:
            s3_path = S3Path(filename)
            self.s3_gateway.delete_object(s3_path.bucket, s3_path.key)
        else:
            raise ValueError("The file is not an s3 file")

    def file_exists(self, filename: str) -> bool:
        if StorageService.path_type(filename) == PathType.S3:
            s3_path = S3Path(filename)
            return self.s3_gateway.object_exists(s3_path.bucket, s3_path.key)
        else:
            raise ValueError(f"File {filename} is not an S3 filepath")

    def get_file_info(self, filename: str) -> FileInfo:
        """Show file information (last modified time, type and size)
        Keyword arguments:
        filename -- the s3 file to be shown
        """
        s3_path = S3Path(filename)
        file_info_dict = self.s3_gateway.get_object_info(s3_path.bucket, s3_path.key)
        return FileInfo(
            file_name=filename,
            last_modified=file_info_dict.get("LastModified").ctime(),
            file_size=file_info_dict.get("ContentLength"),
        )

    def get_file_size(self, filename: str) -> int:
        s3_path = S3Path(filename)
        return self.s3_gateway.get_object_size(s3_path.bucket, s3_path.key)

    def list_folders(self, filename: str) -> List[str]:
        s3_path = S3Path(filename)
        return self.s3_gateway.list_folders(s3_path.bucket, s3_path.key)
