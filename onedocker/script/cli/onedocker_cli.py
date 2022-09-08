#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


"""
CLI for uploading an executable to one docker repo


Usage:
    onedocker-cli upload --config=<config> --package_name=<package_name> --package_path=<package_path> --version=<version>
    onedocker-cli archive --config=<config> --package_name=<package_name> [--version=<version> ] [options]
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
from onedocker.repository.onedocker_repository_service import OneDockerRepositoryService

logger = None
onedocker_svc = None
container_svc = None
onedocker_repo_svc = None
log_svc = None
task_definition = None
repository_path = None
storage_svc = None

DEFAULT_TIMEOUT = 18000


def _upload(
    package_path: str,
    package_name: str,
    version: str,
) -> None:
    logger.info(
        f" Starting uploading package {package_name} at '{package_path}', version {version}..."
    )
    logger.info(f"Uploading binary for package {package_name}: {version}")
    onedocker_repo_svc.upload(package_name, version, package_path)
    logger.info(f" Finished uploading '{package_name}, version {version}'.\n")


def _archive(
    package_name: str,
    version: str,
) -> None:
    logger.info(f" Starting archiving package {package_name} version {version}...")
    logger.info(f"Archiving binary for package {package_name}: {version}")
    onedocker_repo_svc.archive_package(package_name, version)
    logger.info(f" Finished Archiving '{package_name}, version {version}'.\n")


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
        package_info = onedocker_repo_svc.package_repo.get_package_info(
            package_name, version
        )
        print(
            f" Package [{package_info.package_name}], version {package_info.version}: Last modified: {package_info.last_modified}; Size: {package_info.package_size} bytes"
        )
    else:
        package_versions = onedocker_repo_svc.package_repo.get_package_versions(
            package_name
        )
        print(
            f" All available versions for package {package_name} : {package_versions}"
        )
        for version in package_versions:
            package_info = onedocker_repo_svc.package_repo.get_package_info(
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
    config_dependency: Optional[Dict[str, Any]] = config.get("dependency")
    if not config_dependency or "StorageService" not in config_dependency:
        raise KeyError("StorageService is absent in the config.")
    storage_svc_config: Dict[str, Any] = config_dependency["StorageService"]
    storage_class = reflect.get_class(storage_svc_config["class"])
    return storage_class(**storage_svc_config["constructor"])


def _build_container_service(config: Dict[str, Any]) -> ContainerService:
    config_dependency: Optional[Dict[str, Any]] = config.get("dependency")
    if not config_dependency or "ContainerService" not in config_dependency:
        raise KeyError("ContainerService is absent in the config.")
    container_svc_config: Dict[str, Any] = config_dependency["ContainerService"]
    container_class = reflect.get_class(container_svc_config["class"])
    return container_class(**container_svc_config["constructor"])


def _build_log_service(config: Dict[str, Any]) -> LogService:
    config_dependency: Optional[Dict[str, Any]] = config.get("dependency")
    if not config_dependency or "LogService" not in config_dependency:
        raise KeyError("LogService is absent in the config.")
    log_svc_config: Dict[str, Any] = config_dependency["LogService"]
    log_class = reflect.get_class(log_svc_config["class"])
    return log_class(**log_svc_config["constructor"])


def _build_exe_s3_path(repository_path: str, package_name: str, version: str) -> str:
    return f"{repository_path}{package_name}/{version}/{package_name.split('/')[-1]}"


def _build_repo_service(config: Dict[str, Any]) -> OneDockerRepositoryService:
    config_setting: Optional[Dict[str, str]] = config.get("setting")
    if not config_setting or "repository_path" not in config_setting:
        raise KeyError("repository_path is absent in the config.")
    storage_svc = _build_storage_service(config)
    return OneDockerRepositoryService(storage_svc, config_setting["repository_path"])


def _build_onedocker_service(config: Dict[str, Any], container_svc) -> OneDockerService:
    config_setting: Optional[Dict[str, str]] = config.get("setting")
    if not config_setting or "task_definition" not in config_setting:
        raise KeyError("task_definition is absent in the config.")
    return OneDockerService(container_svc, config_setting["task_definition"])


def main() -> None:
    global container_svc, onedocker_svc, onedocker_repo_svc, log_svc, logger, task_definition, repository_path, storage_svc
    s = schema.Schema(
        {
            "upload": bool,
            "test": bool,
            "show": bool,
            "stop": bool,
            "archive": bool,
            "--verbose": bool,
            "--help": bool,
            "--config": schema.And(schema.Use(PurePath), os.path.exists),
            "--package_name": schema.Or(None, schema.And(str, len)),
            "--package_path": schema.Or(None, schema.And(str, len)),
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
    package_path = arguments["--package_path"]
    version = arguments["--version"]

    config = yaml.load(Path(arguments["--config"])).get("onedocker-cli")

    if arguments["upload"]:
        onedocker_repo_svc = _build_repo_service(config)
        _upload(package_path, package_name, version)
    elif arguments["archive"]:
        onedocker_repo_svc = _build_repo_service(config)
        _archive(package_name, version)
    elif arguments["test"]:
        container_svc = _build_container_service(config)
        onedocker_svc = _build_onedocker_service(config, container_svc)
        log_svc = _build_log_service(config)
        timeout = arguments["--timeout"] if arguments["--timeout"] else DEFAULT_TIMEOUT
        _test(package_name, version, arguments["--cmd_args"], timeout)
    elif arguments["show"]:
        onedocker_repo_svc = _build_repo_service(config)
        _show(package_name, arguments["--version"])
    elif arguments["stop"]:
        container_svc = _build_container_service(config)
        onedocker_svc = _build_onedocker_service(config, container_svc)
        _stop(arguments["--container"])


if __name__ == "__main__":
    main()
