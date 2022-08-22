# Change log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
### Changed
### Removed

## [0.3.0] - 2022-08-22
### Added
- Add ContainerType enity for different types of containers
### Removed
- Remove unrelated API validate_container_definition out of container service

---
> Older releases are below this line. We're changing the changelog format for better readability. The latest release log should be at the top.

## 0.3.0 -> 0.3.1
### Types of changes
*  New feature (non-breaking change which adds functionality)

### Description of changes
Add parameter to ContainerService/OneDockerService to allow passing in environment variables

## 0.3.1 -> 0.3.2
### Types of changes
*  New feature (non-breaking change which adds functionality)

### Description of changes
Add optional task_definition member to OneDockerService and introduce task_definition as a param for start_container functions

## 0.3.2 -> 0.4.0
### Types of changes
*  Breaking change

### Description of changes
Deprecate container_version parameter for OneDockerService start_container functions

## 0.4.0 -> 0.1.0
### Types of changes
* Breaking change

### Description of changes
To unblock GTM(Go To Market), we want to rename our project to fbpcp and re-release it to Github and Pypi, the original fbpcs will refer to [Facebook Private Computation Solutions](https://github.com/facebookresearch/fbpcs)

## 0.1.0 -> 0.1.1
### Types of changes
*  Breaking change

### Description of changes
Pass in party instead of role to lift compute stage

## 0.1.1 -> 0.1.2
### Types of changes
*  Breaking change

### Description of changes
Deprecate MPCRole

## 0.1.2 -> 0.1.3
### Types of changes
*  New feature (non-breaking change which adds functionality)

### Description of changes
Add onodocker_cli that can be used to upload/show onedocker repository package, as long as test/stop containers.

## 0.1.3 -> 0.1.4
### Types of changes
*  New feature (non-breaking change which adds functionality)

### Description of changes
Add support for single-word OneDocker package in OneDocker Runner

## 0.1.4 -> 0.1.5
### Types of changes
*  Breaking change

## 0.1.5 -> 0.1.6
### Types of changes
*  Bug fix

### Description of changes
Bug fix in onedocker service to add missing binary version when start containers

## 0.1.6 -> 0.2.0
### Types of changes
*  New feature (non-breaking change which adds functionality)

### Description of changes
Release PCE validator and update onedocker dependencies

## 0.2.0 -> 0.2.1
### Types of changes
* New feature (non-breaking change which adds functionality)

### Description of changes
* API change: get_containers and get_instances now allows optional value
* Add more logging in gateway level for better debugging

## 0.2.1 -> 0.2.2
### Types of changes
* Dependencies Updates

### Description of changes
* Update the version of dependencies to make them internally consistent and Fix the docker image vulnerables

## 0.2.2 -> 0.2.3
### Types of changes
* New feature (non-breaking change which adds functionality)

### Description of changes
* API change: Update get_instances in AWS Container Service to take larger input size

## 0.2.3 -> 0.2.4
### Types of changes
* New feature (non-breaking change which adds functionality)

### Description of changes
* PCE Validator CLI Change: Implement returning non zero exit code for error results

## 0.2.4 -> 0.2.5
### Types of changes
* Bug fix (non-breaking change which fixes an issue)

### Description of changes
* Fixes bug introduced in 0.2.4 (And 0.2.4 was deleted from pypi to prevent further usage)
* The fix is to use the correct parameter name nextToken in list_task_definitions - PR # 252
* (From 0.2.3 -> 0.2.4) PCE Validator CLI Change: Implement returning non zero exit code for error results

## 0.2.5 -> 0.2.6
### Types of changes
* Bug fix (non-breaking change which fixes an issue)

### Description of changes
* Updated the instance updating logic in MPC service

## 0.2.6 -> 0.2.7
### Types of changes
* New feature (non-breaking change which adds functionality)

### Description of changes
* Update the API in MPC Service to take envrionment variables to support onedocker package repository overrides.

## 0.2.7 -> 0.2.8
### Types of changes
* New feature (non-breaking change which adds functionality)

### Description of changes
* Added support for skipping some validation steps in PCE Validator with the --skip-step CLI params

## 0.2.8 -> 0.2.9
### Types of changes
* New feature (non-breaking change which adds functionality)

### Description of changes
* Add get_cluster function to OneDocker Service. Moves towards converting container_svc from public to private attribute.

## 0.2.9 -> 0.2.10
### Types of changes
* New feature (non-breaking change which adds functionality)

### Description of changes
* Add optional session_token field to the AWSContainerService and S3StorageService

## 0.2.10 -> 0.2.11
### Types of changes
* Third-party library version updates

### Description of changes
* Update the cryptography version to match the internal version used.
