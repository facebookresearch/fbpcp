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
