# home-ca

Generate a Certificate Authority and server certificates for a home network.

## Installation

1. Clone this repository.

2. Set up a python virtual environment with:

    ```bash
    python -m venv --prompt home-ca .venv
    ```

3. Source the virtual environment with:

    ```bash
    source .venv/bin/activate
    ```

4. Install required packages using `pip`:

    ```bash
    pip install --upgrade pip pip-tools
    pip-sync
    ```

## How to Use

1. Create a `config.yaml` file to match your environment.  There is a `sample-config.yaml` to use as a template.

2. Run the script with:

    ```bash
    python -m home_ca
    ```

    You can specify a different configuration file using the `-f` or `--config-file` flag:

    ```bash
    python -m home_ca --config-file other-network.yaml
    ```

    The script will output certificates and keys to the `certificates` directory.  This can be change in the configuration file or by using the `-o` or `--output-directory` command line flag.

    The CA will have two files:
    - `ca.key.pem` - the private key
    - `ca.cert.pem` - the CA certificate

    Each server will have three files:
    - `<server>.key.pem` - the private key
    - `<server>.cert.pem` - the signed server certificate
    - `<server>.chain.pem` - the full certificate chain for the server

3. _Optional -_ Use the `validate-certificates.sh` and `display-certificates.sh` scripts to validate the output.  These scripts take a directory as an optional argument; if none is supplied they look in the `certificates` directory.

4. Install `ca.cert.pem` file from the `certificates` directory in any clients, e.g. using _Keychain Access_.

5. Install the server certificates and keys as appropriate for each server, e.g.:
    - [Synology](https://kb.synology.com/en-nz/DSM/help/DSM/AdminCenter/connection_certificate)
    - [Unifi Docker Container](https://github.com/jacobalberty/unifi-docker?tab=readme-ov-file#certificate-support)

## References

- [`pyca/cryptography` documentation](https://cryptography.io/en/latest/x509/tutorial/#creating-a-ca-hierarchy)
