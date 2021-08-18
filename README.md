# FBPCP (Facebook Private Computation Platform)
[Secure multi-party computation](https://en.wikipedia.org/wiki/Secure_multi-party_computation) (also known as secure computation, multi-party computation (MPC), or privacy-preserving computation) is a subfield of cryptography with the goal of creating methods for parties to jointly compute a function over their inputs while keeping those inputs private.

FBPCP (Facebook Private Computation Platform) is a secure, privacy safe and scalable architecture to deploy MPC (Multi Party Computation) applications in a distributed way on virtual private clouds. [FBPCF](https://github.com/facebookresearch/fbpcf) (Facebook Private Computation Framework) is for scaling MPC computation up via threading, while FBPCP is for scaling MPC computation out via [Private Scaling](https://github.com/facebookresearch/fbpcp/blob/main/docs/PrivateScaling.md) architecture. FBPCP consists of various services, interfaces that enable various private measurement solutions, e.g. [Private Lift](https://github.com/facebookresearch/fbpcf/blob/master/docs/PrivateLift.md).

[Private Scaling](https://github.com/facebookresearch/fbpcp/blob/main/docs/PrivateScaling.md) resembles the map/reduce architecture and is secure against a semi-honest adversary who tries to learn the inputs of the computation. The goal is to secure the intermediate output of each shard to prevent potential privacy leak.

## Installation Requirements:
### Prerequisites for working on Ubuntu 18.04:
* An AWS account (Access Key ID, Secret Access Key) to use AWS SDK (boto3 API) in FBPCP
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
## Installing fbpcp
```sh
python3.8 -m pip install 'git+https://github.com/facebookresearch/fbpcp.git'
# (add --user if you don't have permission)

# Or, to install it from a local clone:
git clone https://github.com/facebookresearch/fbpcp.git
python3.8 -m pip install -e fbpcp
# (add --user if you don't have permission)

# Or, to install it from Pypi
python3.8 -m pip install fbpcp
```

## Upgrading fbpcp
* To latest version in github main branch
```sh
python3.8 -m pip uninstall fbpcp
# uninstall fbpcp first

python3.8 -m pip install 'git+https://github.com/facebookresearch/fbpcp.git'
# (add --user if you don't have permission)
# re-install fbpcp from github repository
```

* To latest version in Pypi
```sh
python3.8 -m pip install fbpcp --upgrade
```

## Architecture
<img src="https://github.com/facebookresearch/fbpcp/blob/main/docs/PCPArch.jpg?raw=true" alt="Figure 1: Architecture of FBPCP" width="50%" height="50%">

### Services:

* MPCService is the public interface that provides APIs to distribute a MPC application with large dataset to multiple MPC workers on cloud.


### [Other components](https://github.com/facebookresearch/fbpcp/blob/main/docs/FBPCPComponents.md)

## Join the FBPCP community
* Website: https://github.com/facebookresearch/fbpcp
* See the [CONTRIBUTING](https://github.com/facebookresearch/fbpcp/blob/main/CONTRIBUTING.md) file for how to help out.

## License
FBPCP is [MIT](https://github.com/facebookresearch/fbpcp/blob/main/LICENSE) licensed, as found in the LICENSE file.
