#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json
import unittest
import uuid
from unittest.mock import Mock, patch

from fbpcs.entity.container_instance import ContainerInstance, ContainerInstanceStatus
from fbpcs.error.owdl import OWDLRuntimeError
from onedocker.onedocker_lib.entity.owdl_state import OWDLState
from onedocker.onedocker_lib.entity.owdl_state_instance import Status as StateStatus
from onedocker.onedocker_lib.entity.owdl_workflow import OWDLWorkflow
from onedocker.onedocker_lib.entity.owdl_workflow_instance import (
    Status as WorkflowStatus,
)
from onedocker.onedocker_lib.repository.owdl_workflow_instance_local import (
    LocalOWDLWorkflowInstanceRepository,
)
from onedocker.onedocker_lib.service.owdl_driver import OWDLDriver


class TestOWDLDriver(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        repo_patcher = patch(
            "onedocker.onedocker_lib.repository.owdl_workflow_instance.OWDLWorkflowInstanceRepository"
        )
        cls.instance_repo = repo_patcher.start()

        cls.onedocker_svc = patch("fbpcs.service.onedocker.OneDockerService").start()

    def setUp(self):
        self.mocked_container_info = [
            ContainerInstance(
                instance_id="arn:aws:ecs:us-west-2:592513842793:task/pl-cluster-amazon-demo/a63884bbdf9143cba089a15e8213ccdd",
                ip_address="10.0.21.39",
                status=ContainerInstanceStatus.STARTED,
            )
        ]
        self.rand_id = str(uuid.uuid4())
        self.mocked_container_info = [
            ContainerInstance(
                instance_id="arn:aws:ecs:us-west-2:592513842793:task/pl-cluster-amazon-demo/a63884bbdf9143cba089a15e8213ccdd",
                ip_address="10.0.21.39",
                status=ContainerInstanceStatus.STARTED,
            )
        ]

        lift = OWDLState(
            "Task",
            "onedocker-cli-test:2#onedocker-cli-test",
            "ziyan-test/lift",
            [
                "--role=1 --input_filenames=ziyan/pl_test/mpc_computed_publisher.csv_prepared_0 --input_directory=https://private-identity-tests-test.s3.us-west-2.amazonaws.com/ --output_filenames=ziyan/pl_test/test/mpc_computed_publisher.csv --output_directory=https://private-identity-tests-test.s3.us-west-2.amazonaws.com/ --concurrency=1"
            ],
            None,
            end=True,
        )

        self.workflow = OWDLWorkflow("Lift", {"Lift": lift}, None)

    def test_driver_single_container(self):
        self.onedocker_svc.start_containers = Mock(
            return_value=self.mocked_container_info
        )
        self.onedocker_svc.get_containers = Mock(
            return_value=self.mocked_container_info
        )

        driver = OWDLDriver(
            self.onedocker_svc, self.instance_repo, self.rand_id, self.workflow
        )
        driver.start()

        driver.get_status()
        self.assertEqual(
            driver.get_current_state_instance().status, StateStatus.STARTED
        )
        self.assertEqual(driver.get_status().status, WorkflowStatus.STARTED)

    def test_driver_no_repo(self):
        with self.assertRaises(OWDLRuntimeError):
            driver = OWDLDriver(  # noqa: F841
                self.onedocker_svc, None, self.rand_id, self.workflow
            )

    def test_driver_multiple_containers(self):
        mocked_container_info_get = [
            [
                ContainerInstance(
                    instance_id="arn:aws:ecs:us-west-2:592513842793:task/pl-cluster-amazon-demo/a63884bbdf9143cba089a15e8213ccdd",
                    ip_address="10.0.21.39",
                    status=ContainerInstanceStatus.COMPLETED,
                )
            ],
            [
                ContainerInstance(
                    instance_id="arn:aws:ecs:us-west-2:592513842793:task/pl-cluster-amazon-demo/a63884bbdf9143cba089a15e8213ccdd",
                    ip_address="10.0.21.39",
                    status=ContainerInstanceStatus.STARTED,
                )
            ],
            [
                ContainerInstance(
                    instance_id="arn:aws:ecs:us-west-2:592513842793:task/pl-cluster-amazon-demo/a63884bbdf9143cba089a15e8213ccdd",
                    ip_address="10.0.21.39",
                    status=ContainerInstanceStatus.STARTED,
                )
            ],
        ]
        mocked_container_info_start = self.mocked_container_info
        lift = OWDLState(
            "Task",
            "onedocker-cli-test:2#onedocker-cli-test",
            "ziyan-test/lift",
            [
                "--role=1 --input_filenames=ziyan/pl_test/mpc_computed_publisher.csv_prepared_0 --input_directory=https://private-identity-tests-test.s3.us-west-2.amazonaws.com/ --output_filenames=ziyan/pl_test/test/mpc_computed_publisher.csv --output_directory=https://private-identity-tests-test.s3.us-west-2.amazonaws.com/ --concurrency=1"
            ],
            None,
            "Attribution",
        )
        attribution = OWDLState(
            "Task",
            "onedocker-cli-test:2#onedocker-cli-test",
            "private_attribution/attribution",
            [""],
            None,
            end=True,
        )

        workflow = OWDLWorkflow(
            "Lift", {"Lift": lift, "Attribution": attribution}, None
        )

        self.onedocker_svc.start_containers = Mock(
            return_value=mocked_container_info_start
        )
        self.onedocker_svc.get_containers = Mock()
        self.onedocker_svc.get_containers.side_effect = mocked_container_info_get

        driver = OWDLDriver(
            self.onedocker_svc, self.instance_repo, self.rand_id, workflow
        )
        driver.start()
        driver.get_status()
        driver.next()  # noqa: B305

        driver.get_status()
        self.assertEqual(
            driver.get_current_state_instance().status, StateStatus.STARTED
        )
        self.assertEqual(driver.get_status().status, WorkflowStatus.STARTED)

    def test_driver_state_failed(self):
        self.mocked_container_info[0].status = ContainerInstanceStatus.FAILED
        self.onedocker_svc.start_containers = Mock(
            return_value=self.mocked_container_info
        )
        self.onedocker_svc.get_containers = Mock(
            return_value=self.mocked_container_info
        )

        driver = OWDLDriver(
            self.onedocker_svc, self.instance_repo, self.rand_id, self.workflow
        )
        driver.start()

        driver.get_status()
        self.assertEqual(
            driver.get_current_state_instance().status,
            StateStatus.FAILED,
            driver.owdl_workflow_instance.state_instances[-1].containers[-1].status,
        )
        self.assertEqual(driver.get_status().status, WorkflowStatus.FAILED)

    def test_driver_cancelled_state(self):
        self.onedocker_svc.start_containers = Mock(
            return_value=self.mocked_container_info
        )

        driver = OWDLDriver(
            self.onedocker_svc, self.instance_repo, self.rand_id, self.workflow
        )
        driver.start()
        driver.cancel_state()

        driver.get_status()
        self.assertEqual(
            driver.get_current_state_instance().status,
            StateStatus.CANCELLED,
            driver.owdl_workflow_instance.state_instances[-1].containers[-1].status,
        )
        self.assertEqual(driver.get_status().status, WorkflowStatus.STARTED)

    def test_driver_cancelled_workflow(self):
        self.onedocker_svc.start_containers = Mock(
            return_value=self.mocked_container_info
        )

        driver = OWDLDriver(
            self.onedocker_svc, self.instance_repo, self.rand_id, self.workflow
        )
        driver.start()
        driver.cancel_workflow()

        self.assertEqual(driver.get_status().status, WorkflowStatus.CANCELLED)

    def test_driver_stopped_container(self):
        mocked_container_info_get = [
            ContainerInstance(
                instance_id="arn:aws:ecs:us-west-2:592513842793:task/pl-cluster-amazon-demo/a63884bbdf9143cba089a15e8213ccdd",
                ip_address="10.0.21.39",
                status=ContainerInstanceStatus.FAILED,
            )
        ]

        self.onedocker_svc.start_containers = Mock(
            return_value=self.mocked_container_info
        )
        self.onedocker_svc.get_containers = Mock(return_value=mocked_container_info_get)

        driver = OWDLDriver(
            self.onedocker_svc, self.instance_repo, self.rand_id, self.workflow
        )
        driver.start()
        instance_ids = [
            container.instance_id
            for container in driver.owdl_workflow_instance.state_instances[
                -1
            ].containers
        ]

        self.onedocker_svc.stop_containers(instance_ids)

        driver.get_status()
        self.assertEqual(
            driver.get_current_state_instance().status,
            StateStatus.FAILED,
            driver.owdl_workflow_instance.state_instances[-1].containers[-1].status,
        )
        self.assertEqual(driver.get_status().status, WorkflowStatus.FAILED)

    def test_driver_existing_workflow_instance(self):
        self.onedocker_svc.start_containers = Mock(
            return_value=self.mocked_container_info
        )
        self.onedocker_svc.get_containers = Mock(
            return_value=self.mocked_container_info
        )
        self.onedocker_svc.stop_containers = Mock()

        instance_repo = LocalOWDLWorkflowInstanceRepository("/tmp/")
        driver = OWDLDriver(
            self.onedocker_svc, instance_repo, self.rand_id, self.workflow
        )
        driver.start()
        driver.cancel_workflow()

        # patternlint-disable-next-line f-string-may-be-missing-leading-f
        workflow_inst = """{"owdl_workflow": {"States": {"Lift": {"Next": null, "End": true, "Version": null, "Type": "Task", "PackageName": "ziyan-test/lift", "ContainerDefinition": "onedocker-cli-test:2#onedocker-cli-test", "CmdArgsList": ["--role=1 --input_filenames=ziyan/pl_test/mpc_computed_publisher.csv_prepared_0 --input_directory=https://private-identity-tests-test.s3.us-west-2.amazonaws.com/ --output_filenames=ziyan/pl_test/test/mpc_computed_publisher.csv --output_directory=https://private-identity-tests-test.s3.us-west-2.amazonaws.com/ --concurrency=1"], "Timeout": null}}, "Version": null, "StartAt": "Lift"}, "status": "CREATED", "instance_id": "ncdnowrw", "state_instances": []}"""
        instance_repo.read_instance = Mock(return_value=json.loads(workflow_inst))

        driver2 = OWDLDriver(self.onedocker_svc, instance_repo, self.rand_id, None)
        driver2.start()
        instance_repo.delete(self.rand_id)
        driver2.get_status()
        self.assertEqual(
            driver2.get_current_state_instance().status,
            StateStatus.STARTED,
        )
        self.assertEqual(driver2.get_status().status, WorkflowStatus.STARTED)

    def test_driver_retry(self):
        self.workflow.states["Lift"].retry_count = 1

        self.onedocker_svc.start_containers = Mock(
            return_value=self.mocked_container_info
        )
        self.onedocker_svc.get_containers = Mock(
            return_value=self.mocked_container_info
        )

        driver = OWDLDriver(
            self.onedocker_svc, self.instance_repo, self.rand_id, self.workflow
        )
        driver.start()
        driver.cancel_state()
        self.assertEqual(0, driver.get_current_retry_num())
        driver.retry()

        driver.get_status()
        self.assertEqual(1, driver.get_current_retry_num())
        self.assertEqual(2, len(driver.get_status().state_instances))
