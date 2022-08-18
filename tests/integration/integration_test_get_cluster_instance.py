#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import asyncio

from fbpcp.intern.service.container_aws_fb import FBAWSContainerService

from measurement.private_measurement.pcp.pce.scripts.pce_service_client import (
    PCEServiceClient,
)

ACCOUNT = "482880953677"
TEST_PARTNER_ID = "pce-monitor-test"


async def test_get_cluster_details() -> None:
    client = PCEServiceClient("STAGING")
    pce_instances = await client.get_pce_for_partner(TEST_PARTNER_ID)
    if not pce_instances:
        raise Exception("Test not setup correctly, no pce instance")
    instance = pce_instances[0]
    container_svc = FBAWSContainerService(
        region=instance.metadata.cloud_region,
        cluster=instance.pce.cluster_name,
        subnets=list(instance.pce.subnet_ids),
        account=ACCOUNT,
    )
    cmd = ["echo hello"] * 5
    container_svc.create_instances(instance.pce.container_definition_id, cmd)

    cluster_instance = container_svc.get_cluster_instance()
    print(
        f"cluster-name: {cluster_instance.cluster_name}, pending tasks:{cluster_instance.pending_tasks}, running tasks: {cluster_instance.running_tasks}, status: {cluster_instance.status}"
    )


if __name__ == "__main__":
    asyncio.run(test_get_cluster_details())
