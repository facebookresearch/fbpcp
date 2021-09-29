#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict
from enum import Enum


class ServiceName(Enum):
    AWS_MACIE = "Amazon Macie"
    AWS_S3 = "Amazon Simple Storage Service"
    AWS_CLOUDTRAIL = "AWS CloudTrail"
    AWS_COST_EXPLORER = "AWS Cost Explorer"
    AWS_EC2 = "Amazon Elastic Compute Cloud - Compute"
    AWS_EC2_OTHER = "EC2 - Other"
    AWS_DYNAMODB = "Amazon DynamoDB"
    AWS_ECS = "Amazon Elastic Container Service"
    AWS_SNS = "Amazon Simple Notification Service"
    AWS_ELB = "Amazon Elastic Load Balancing"
    AWS_LAMBDA = "AWS Lambda"
    AWS_CLOUDWATCH_EVENTS = "CloudWatch Events"
    AWS_CLOUDWATCH = "AmazonCloudWatch"
    AWS_SQS = "Amazon Simple Queue Service"
    AWS_GUARDDUTY = "Amazon GuardDuty"
    AWS_BACKUP = "AWS Backup"
    AWS_KMS = "AWS Key Management Service"
    AWS_TAX = "Tax"
    AWS_KINESIS = "Amazon Kinesis Firehose"
    AWS_GLUE = "AWS Glue"
    AWS_EFS = "Amazon Elastic File System"
    AWS_SECRETS_MANAGER = "AWS Secrets Manager"
    AWS_ECR = "Amazon EC2 Container Registry (ECR)"
    AWS_CONFIG = "AWS Config"
