#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


"""
CLI for uploading an executable to one docker repo


Usage:
    onedocker-cli upload --config=<config> --package_name=<package_name> --package_dir=<package_dir> [--version=<version> --enable_attestation] [options]
    onedocker-cli test --config=<config> --package_name=<package_name> --cmd_args=<cmd_args> [--version=<version> --timeout=<timeout>][options]
    onedocker-cli show --config=<config> --package_name=<package_name> [--version=<version>] [options]
    onedocker-cli stop --config=<config> --container=<container_id> [options]

Options:
    -h --help                Show this help
    --log_path=<path>        Override the default path where logs are saved
    --verbose                Set logging level to DEBUG
"""

import asyncio
import logging
import os
import time
from pathlib import Path, PurePath
from typing import Any, Dict, Optional

import schema
from docopt import docopt
from fbpcp.entity.container_instance import ContainerInstanceStatus
from fbpcp.service.container import ContainerService
from fbpcp.service.log import LogService
from fbpcp.service.onedocker import OneDockerService
from fbpcp.service.storage import StorageService
from fbpcp.util import reflect, yaml
from onedocker.repository.onedocker_checksum import OneDockerChecksumRepository
from onedocker.repository.onedocker_package import OneDockerPackageRepository
from onedocker.service.attestation import AttestationService

logger = None

attestation_svc = None
container_svc = None
onedocker_svc = None
log_svc = None

onedocker_checksum_repo = None
onedocker_package_repo = None

DEFAULT_BINARY_VERSION = "latest"
DEFAULT_TIMEOUT = 18000


def _upload(
    package_dir: str,
    package_name: str,
    version: str,
    enable_attestation: bool = False,
) -> None:
    logger.info(
        f" Starting uploading package {package_name} at '{package_dir}', version {version}..."
    )
    if enable_attestation:
        logger.info(f"Generating checksums for package {package_name}: {version}")
        formatted_checksum_info = attestation_svc.track_binary(
            binary_path=package_dir,
            package_name=package_name,
            version=version,
        )
        logger.info(f"Uploading checksums for package {package_name}: {version}")
        onedocker_checksum_repo.write(
            package_name=package_name,
            version=version,
            checksum_data=formatted_checksum_info,
        )
    logger.info(f"Uploading binary for package {package_name}: {version}")
    onedocker_package_repo.upload(package_name, version, package_dir)
    logger.info(f" Finished uploading '{package_name}, version {version}'.\n")


def _test(
    package_name: str,
    version: str,
    cmd_args: str,
    timeout: int,
) -> None:
    logger.info(" Running test container ...")
    container = onedocker_svc.start_container(
        package_name=package_name,
        version=version,
        cmd_args=cmd_args,
        timeout=DEFAULT_TIMEOUT,
    )
    container = asyncio.run(
        onedocker_svc.wait_for_pending_container(container.instance_id)
    )
    logger.info(container)
    log_path = log_svc.get_log_path(container)
    start_time = 0
    while container.status == ContainerInstanceStatus.STARTED:
        container = container_svc.get_instance(container.instance_id)
        if not container:
            raise ValueError(
                f"An error was raised while getting a container with id: {container.instance_id}, got None."
            )

        log_events = log_svc.fetch(log_path, start_time)

        for event in log_events:
            logger.info(event.message)

        if log_events:
            start_time = log_events[-1].timestamp + 1
        # temparorily set the process to be periodlly fetching and showing the log
        time.sleep(5)


def _show(
    package_name: str,
    version: Optional[str] = None,
) -> None:
    logger.info(
        f"Show package [{package_name}], version {version} information on storage "
    )

    if version:
        package_info = onedocker_package_repo.get_package_info(package_name, version)
        print(
            f" Package [{package_info.package_name}], version {package_info.version}: Last modified: {package_info.last_modified}; Size: {package_info.package_size} bytes"
        )
    else:
        package_versions = onedocker_package_repo.get_package_versions(package_name)
        print(
            f" All available versions for package {package_name} : {package_versions}"
        )
        for version in package_versions:
            package_info = onedocker_package_repo.get_package_info(
                package_name, version
            )
            print(
                f"Package [{package_info.package_name}], version {package_info.version}: Last modified: {package_info.last_modified}; Size: {package_info.package_size} bytes"
            )


def _stop(container_id: str) -> None:
    logger.info(f"Stopping container {container_id} ...")
    errors = onedocker_svc.stop_containers([container_id])
    if errors[0] is None:
        logger.info(f"Container {container_id} has been stopped")
    else:
        logger.info(
            f"Encountered errors when stopping container {container_id}: {errors[0]}"
        )


def _build_storage_service(config: Dict[str, Any]) -> StorageService:
    storage_class = reflect.get_class(config["class"])
    return storage_class(**config["constructor"])


def _build_container_service(config: Dict[str, Any]) -> ContainerService:
    container_class = reflect.get_class(config["class"])
    return container_class(**config["constructor"])


def _build_log_service(config: Dict[str, Any]) -> LogService:
    log_class = reflect.get_class(config["class"])
    return log_class(**config["constructor"])


def main() -> None:
    global container_svc, onedocker_svc, onedocker_package_repo, onedocker_checksum_repo, log_svc, logger, attestation_svc
    s = schema.Schema(
        {
            "upload": bool,
            "test": bool,
            "show": bool,
            "stop": bool,
            "--verbose": bool,
            "--help": bool,
            "--enable_attestation": bool,
            "--config": schema.And(schema.Use(PurePath), os.path.exists),
            "--package_name": schema.Or(None, schema.And(str, len)),
            "--package_dir": schema.Or(None, schema.And(str, len)),
            "--cmd_args": schema.Or(None, schema.And(str, len)),
            "--container": schema.Or(None, schema.And(str, len)),
            "--log_path": schema.Or(None, schema.Use(Path)),
            "--version": schema.Or(None, schema.And(str, len)),
            "--timeout": schema.Or(None, schema.Use(int)),
        }
    )

    arguments = s.validate(docopt(__doc__))
    logger = logging.getLogger(__name__)
    log_path = arguments["--log_path"]
    log_level = logging.DEBUG if arguments["--verbose"] else logging.INFO
    logging.basicConfig(filename=log_path, level=log_level)

    package_name = arguments["--package_name"]
    package_dir = arguments["--package_dir"]
    version = (
        arguments["--version"] if arguments["--version"] else DEFAULT_BINARY_VERSION
    )

    config = yaml.load(Path(arguments["--config"])).get("onedocker-cli")

    if arguments["upload"] or arguments["show"]:
        repository_path = config["setting"]["repository_path"]
        checksum_repository_path = config["setting"].get("checksum_repository_path", "")

        storage_svc = _build_storage_service(config["dependency"]["StorageService"])

        onedocker_package_repo = OneDockerPackageRepository(
            storage_svc, repository_path
        )
        if checksum_repository_path:
            onedocker_checksum_repo = OneDockerChecksumRepository(
                storage_svc, checksum_repository_path
            )

    if arguments["test"] or arguments["stop"]:
        task_definition = config["setting"]["task_definition"]
        container_svc = _build_container_service(
            config["dependency"]["ContainerService"]
        )
        onedocker_svc = OneDockerService(container_svc, task_definition)

    if arguments["upload"]:
        enable_attestation = arguments["--enable_attestation"]

        status = "enabled" if enable_attestation else "disabled"
        logger.info(
            f"Package tracking for package {package_name}: {version} is {status}"
        )

        attestation_svc = AttestationService()

        _upload(package_dir, package_name, version, enable_attestation)
    elif arguments["test"]:
        timeout = arguments.get("--timeout", DEFAULT_TIMEOUT)

        log_svc = _build_log_service(config["dependency"]["LogService"])

        _test(package_name, version, arguments["--cmd_args"], timeout)
    elif arguments["show"]:
        _show(package_name, arguments["--version"])
    elif arguments["stop"]:
        _stop(arguments["--container"])


if __name__ == "__main__":
    main()
