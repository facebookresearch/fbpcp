# Change log
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
