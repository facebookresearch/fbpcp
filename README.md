# FBPCS (Facebook Private Computation Service)
[Secure multi-party computation](https://en.wikipedia.org/wiki/Secure_multi-party_computation) (also known as secure computation, multi-party computation (MPC), or privacy-preserving computation) is a subfield of cryptography with the goal of creating methods for parties to jointly compute a function over their inputs while keeping those inputs private.

FBPCS (Facebook Private Computation Service) is a secure, privacy safe and scalable architecture to deploy MPC (Multi Party Computation) applications in a distributed way on virtual private clouds. [FBPCF](https://github.com/facebookresearch/fbpcf) is for scaling MPC vertically, while FBPCS is for scaling MPC horizontally. FBPCS consists of various services, interfaces to support various private measurement products, e.g. [Private Lift](https://github.com/facebookresearch/fbpcf/blob/master/docs/PrivateLift.md).

 [Pirvate Scaling](https://github.com/facebookresearch/FBPCS/blob/main/docs/PrivateScaling.md) is to handle large volumes of data for products like Private Lift that leverage privacy enhancing technologies including multiparty computation games.

## Installation Requirements:
### Prerequisites for working on Ubuntu 18.04:
* An AWS account (Access Key ID, Secret Access Key) to use AWS SDK (boto3 API) in FBPCS
* python >= 3.8
* python3-pip

## Installing prerequisites on Ubuntu 18.04:
* python3.8
```sh
sudo apt-get install -y python3.8
```
* python3-pip
```sh
sudo apt-get install -y python3-pip
```
## Installing fbpcs
```sh
git clone https://github.com/facebookresearch/FBPCS.git
cd FBPCS
sudo python3 pip install -e . --user
```

## Architecture
<img src="https://github.com/facebookresearch/FBPCS/blob/main/docs/PCSArch.jpg?raw=true" alt="Figure 1: Architecture of FBPCS" width="50%" height="50%">

### Services:

* MPC service provides APIs to upstream services like Private Lift to distribute a larger MPC game to multiple MPC workers in containers on specific clusters.

* MPC game service will provide MPC service with executable package name and game arguments, which the containers on clouds will execute while running.

* OneDocker service is responsible for executing executable(s) in a container on clouds. It will generate the commands input in the bash and trigger the containers to execute the executable(s).

### [Other components](https://github.com/facebookresearch/FBPCS/blob/main/docs/FBPCSComponents.md)

## License
FBPCS is [MIT](LICENSE) licensed, as found in the LICENSE file.
