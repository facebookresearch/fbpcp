### Components:
Facebook Private Computation Service follows MVCS( Model View Controller Service) design pattern.

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

Cluster Instance contains information about a cluster on the ECS. For example, the Amazon Resource Name (ARN) that identifies the cluster, the cluster name, etc.

VPC contains information abouot a VPC(virtual Private Cloud) on AWS. For example, the VPC id, state, etc.

### Service:
Service holds all business logic and exposes internal APIs to handlers or internal components within the same code base. Besides MPC Sevice, MPC Game Service and OneDocker Service:

Container Service will take the advantage of ECS gateway and create instances on Amazon ECS for MPC service or other end-point services to use.

Storage Service provides APIs to do CRUD operations on AWS S3 storage.
