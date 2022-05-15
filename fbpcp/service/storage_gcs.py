#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict
import glob
import os
from typing import Any, Dict, List, Optional

from fbpcp.entity.file_information import FileInfo
from fbpcp.entity.policy_statement import PolicyStatement, PublicAccessBlockConfig
from fbpcp.gateway.gcs import GCSGateway
from fbpcp.service.storage import PathType, StorageService
from fbpcp.util.gcspath import GCSPath


class GCSStorageService(StorageService):
    def __init__(
        self,
        credentials_json: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.gcs_gateway = GCSGateway(credentials_json, config)

    def __check_dir(self, local_dir: str) -> None:
        if not os.path.exists(local_dir):
            raise ValueError("directory does not exist: " + local_dir)

    def read(self, filename: str) -> str:
        """Read a file data

        Args:
            filename: fully qualified GCS filename (ex: "https://storage.cloud.google.com/bucket-name/key-name")

        Returns:
            return: file contents as str
        """
        gcs_path = GCSPath(filename)
        return self.gcs_gateway.get_object(gcs_path.bucket, gcs_path.key)

    def write(self, filename: str, data: str) -> None:
        """Write data into a file

        Args:
            filename: fully qualified GCS filename (ex: "https://storage.cloud.google.com/bucket-name/key-name")
            data: file contents as str
        """
        gcs_path = GCSPath(filename)
        return self.gcs_gateway.put_object(gcs_path.bucket, gcs_path.key, data)

    def copy(self, source: str, destination: str, recursive: bool = False) -> None:
        """Move a file or folder between local storage and GCS, or between GCS and GCS

        Args:
            source: source file
            destination: destination file
            recursive: whether to recursively copy a folder

        Raises:
            ValueError: Source is folder and recursive is False
            ValueError: Source is not a valid Local or GCS path
            ValueError: Destination is not a valid Local or GCS path
            ValueError: Both source and destination are the same
            ValueError: Both source and destination are local
        """
        sourceType = StorageService.path_type(source)
        destinationType = StorageService.path_type(destination)
        if sourceType != PathType.GCS and sourceType != PathType.Local:
            raise ValueError("Source is not a valid Local or GCS path")
        if destinationType != PathType.GCS and destinationType != PathType.Local:
            raise ValueError("Destination is not a valid Local or GCS path")
        if source == destination:
            raise ValueError("Both source and destination are the same")

        # source is Local
        if sourceType == PathType.Local:
            if destinationType == PathType.Local:
                raise ValueError("Both source and destination are local files")
            else:
                gcs_path = GCSPath(destination)
                if recursive:
                    self.upload_dir(
                        source=source,
                        gcs_path_bucket=gcs_path.bucket,
                        gcs_path_key=gcs_path.key,
                    )
                else:
                    if os.path.isdir(source):
                        raise ValueError(
                            f"Source {source} is a folder. Use --recursive"
                        )
                    self.gcs_gateway.upload_file(
                        file_name=source, bucket=gcs_path.bucket, key=gcs_path.key
                    )
        # source is GCS
        elif sourceType == PathType.GCS:
            source_gcs_path = GCSPath(source)
            if destinationType == PathType.Local:
                if recursive:
                    self.download_dir(
                        gcs_path_bucket=source_gcs_path.bucket,
                        gcs_path_key=source_gcs_path.key,
                        destination=destination,
                    )
                else:
                    self.gcs_gateway.download_file(
                        bucket=source_gcs_path.bucket,
                        key=source_gcs_path.key,
                        filename=destination,
                    )
            elif destinationType == PathType.GCS:
                destination_gcs_path = GCSPath(destination)
                if recursive:
                    self.copy_dir(
                        source_bucket=source_gcs_path.bucket,
                        source_key=source_gcs_path.key,
                        destination_bucket=destination_gcs_path.bucket,
                        destination_key=destination_gcs_path.key,
                    )
                else:
                    self.gcs_gateway.copy(
                        source_bucket_name=source_gcs_path.bucket,
                        source_key=source_gcs_path.key,
                        dest_bucket_name=destination_gcs_path.bucket,
                        dest_key=destination_gcs_path.key,
                    )

    def upload_dir(self, source: str, gcs_path_bucket: str, gcs_path_key: str) -> None:
        """Upload a directory from the filesystem to GCS

        Args:
            source: source directory (local)
            gcs_path_bucket: GCS bucket
            gcs_path_key: GCS key
        """
        # Check that source directory exists
        self.__check_dir(source)

        # Get list of files
        rel_paths = glob.glob(source + "/**", recursive=True)
        for local_file in rel_paths:
            if os.path.isfile(local_file):
                remote_path = local_file.replace(source, gcs_path_key, 1)
                self.gcs_gateway.upload_file(
                    file_name=local_file, bucket=gcs_path_bucket, key=remote_path
                )

    def download_dir(
        self, gcs_path_bucket: str, gcs_path_key: str, destination: str
    ) -> None:
        """Recursively downloads a directory from GCS to the filesystem

        Args:
            gcs_path_bucket: GCS bucket
            gcs_path_key: GCS key
            destination: destination directory (local)
        """
        # Get list of files
        blob_names = self.gcs_gateway.list_objects(
            bucket=gcs_path_bucket, key=gcs_path_key
        )
        for blob_name in blob_names:
            if blob_name.endswith("/"):
                continue
            file_split = destination.split("/") + blob_name.replace(
                gcs_path_key, "", 1
            ).split("/")
            dir_name = "/".join(file_split[0:-1])
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
            file_name = "/".join(file_split)
            self.gcs_gateway.download_file(
                bucket=gcs_path_bucket, key=blob_name, file_name=file_name
            )

    def copy_dir(
        self,
        source_bucket: str,
        source_key: str,
        destination_bucket: str,
        destination_key: str,
    ) -> None:
        """Copy a directory from GCS to another directory in GCS

        Args:
            source_bucket: Source GCS bucket
            source_key: Source GCS key (directory)
            destination_bucket: Destination GCS bucket
            destination_key: Destination GCS key (directory)

        Raises:
            ValueError: Source and Destination are the same
        """
        if source_bucket == destination_bucket and source_key == destination_key:
            raise ValueError("Source and Destination are the same")

        # Get list of files
        src_blob_names = self.gcs_gateway.list_objects(
            bucket=source_bucket, key=source_key
        )
        dest_key_split = destination_key.split("/")
        for src_blob_name in src_blob_names:
            if src_blob_name.endswith("/"):
                continue
            dest_file_name = "/".join(
                dest_key_split + src_blob_name.replace(source_key, "", 1).split("/")
            )
            self.gcs_gateway.copy(
                source_bucket, src_blob_name, destination_bucket, dest_file_name
            )

    def delete(self, filename: str) -> None:
        """Delete a GCS file

        Args:
            filename: fully qualified GCS filename to be deleted (ex: "https://storage.cloud.google.com/bucket-name/key-name")
        """
        gcs_path = GCSPath(filename)
        return self.gcs_gateway.delete_object(gcs_path.bucket, gcs_path.key)

    def file_exists(self, filename: str) -> bool:
        """Check existence of a GCS file

        Args:
            filename: fully qualified GCS filename to be checked (ex: "https://storage.cloud.google.com/bucket-name/key-name")
        """
        gcs_path = GCSPath(filename)
        return self.gcs_gateway.object_exists(gcs_path.bucket, gcs_path.key)

    def get_file_info(self, filename: str) -> FileInfo:
        """Get file information

        Args:
            filename: fully qualified GCS filename to be inspected (ex: "https://storage.cloud.google.com/bucket-name/key-name")

        Returns:
            FileInfo: file_name, file_size, last_modified
        """
        gcs_path = GCSPath(filename)
        file_info = self.gcs_gateway.get_object_info(gcs_path.bucket, gcs_path.key)
        return FileInfo(
            file_name=filename,
            last_modified=file_info.get("updated"),
            file_size=file_info.get("size"),
        )

    def get_file_size(self, filename: str) -> int:
        """Get file size

        Args:
            filename: fully qualified GCS filename to be inspected (ex: "https://storage.cloud.google.com/bucket-name/key-name")

        Returns:
            int: file size (in bytes)
        """
        gcs_path = GCSPath(filename)
        return self.gcs_gateway.get_object_size(gcs_path.bucket, gcs_path.key)

    def list_folders(self, filename: str) -> List[str]:
        """List folders

        Args:
            filename: fully qualified GCS filename to be inspected (ex: "https://storage.cloud.google.com/bucket-name/key-name")

        Returns:
            List[str]: List of folders found in filename
        """
        folders = []
        gcs_path = GCSPath(filename)
        blob_names = self.gcs_gateway.list_objects(
            bucket=gcs_path.bucket, key=gcs_path.key
        )
        for blob_name in blob_names:
            if blob_name.endswith("/"):
                folders.append(blob_name)
        return folders

    def get_bucket_policy_statements(self, bucket: str) -> List[PolicyStatement]:
        raise NotImplementedError

    def get_bucket_public_access_block(self, bucket: str) -> PublicAccessBlockConfig:
        raise NotImplementedError
