# PCE (Private Computation Environment)
PCE is the environment to run [Multi Party Computation games](https://en.wikipedia.org/wiki/Secure_multi-party_computation). This environment includes two major components: networking and compute.

Networking: a virtual private cloud with subnets, routing table and firewalls setting. In order to keep the communication private, it is also required the two parties virtual clouds can communicate privately.
Compute: a container service with sufficient CPU, memory and enough permissions to interact with other services

## PCE ID:
PCE ID is the identifier for a PCE. It should be unique within a given Cloud account.

# PCE Validator
PCE Validator is to verify above PCE components are set up correctly. It will check all the resources for Networking and Compute are setup correctly and raise warning/error if there is a mis-configuration. Partner can use this tool to verify PCE environment before running a game.

Currently, PCE Validator only supports AWS(Amazon Web Services). You should tag all your resource for the PCE with {"pce:pce-id": "<your-pce-id>"} in order to run validator.

## Installing PCE
You need to install through fbpcp [README](https://github.com/facebookresearch/fbpcp/blob/main/README.md).

## PCE Validator Usage
 python3.8 -m pce.validator --region=<region> --key-id=<key_id> --key-data=<key_data> --pce-id=<pce_id>

Example: for resources tagged with {"pce:pce-id": "test-pce-tag-value"}
 python3.8 -m pce.validator --region=us-west-2 --key-id=AWS_ACCESS_KEY_ID --key-data=AWS_SECRET_ACCESS_KEY --pce-id="test-pce-tag-value"
