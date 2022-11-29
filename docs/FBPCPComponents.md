### Components:
Facebook Private Computation Platform follows [MVCS(Model View Controller Service)](MVCS.md) design pattern.

### Repository
Repository is responsible for encapsulating database-like operations. In our design, we have MPC instance repositories for both Amazon S3 and local storage. The end point service will call MPC service to create an MPC instance and all the files and information related to this instance will be stored on Amazon S3 or local storage, depending on which repository the end point service is using.

### Gateway:
Gateway is responsible for encapsulating the interface of dependent services, which is AWS API in our design. Since we need to run tasks on ECS and store files on S3, it is required to call AWS API to do the operations and these api calls reside in the gateways.

### Mapper:
Mapper deals with data transformation between components. Any response from AWS API calls should be mapped to the data we self defined.

### Entity:
Entity represents business objects, in our case, the MPC Instance, Container Instance and Cluster Instance, etc. In our design:

MPC Instance contains information about a MPC game. For example, MPC game name, ECS fargate containers running the tasks, etc.

Container Instance contains information about a container on an ECS cluster. For example, the instance id, ip address and container status.

### Service:
MPCService is the public interface that FBPCP provides. All other services are internal only so subject to changes.

Service holds all business logic and exposes internal APIs to controllers or other services within the same code base. Besides MPC Sevice, MPC Game Service and OneDocker Service:

* OneDockerService is a cloud agnostic, serverless container management service. Currently, it supports AWS ECS.

* MPCGameService bridges MPCService and OneDockerService together. Given a MPC game and it's arguments, MPCGameService transforms them to OneDocker arguments.

* ContainerService is a generic interface that each cloud may extend to implement a concrete container service. Currently, we support AWS ECS.

* Storage Service provides APIs to do CRUD operations on a particular storage, such as local and S3.
