"""Manage Home CA for Home Network."""

from ipaddress import ip_address
from .config import CONFIG
from . import certs


def main() -> None:
    """Entry point for the script."""
    output_path = CONFIG.output_path

    if not output_path.exists():
        output_path.mkdir()

    ca_key = certs.generate_or_load_key(output_path / 'ca.key.pem')
    ca_cert = certs.generate_or_load_ca_certificate(output_path / 'ca.cert.pem', ca_key)

    for host in CONFIG.hosts:
        name = host.names[0]
        names = [(name if '.' in name else f'{name}.{CONFIG.domain}') for name in host.names] + [ip_address(ip) for ip in host.ip_addresses]

        host_key = certs.generate_or_load_key(output_path / f'{name}.key.pem')
        host_cert = certs.generate_or_load_server_certificate(
            output_path / f'{name}.cert.pem',
            ca_cert,
            ca_key,
            host_key,
            names
        )

        chain_file = output_path / f'{name}.fullchain.pem'

        if not chain_file.exists():
            with chain_file.open(mode='wb') as file:
                file.write(certs.serialize_certificate(host_cert))
                file.write(certs.serialize_certificate(ca_cert))

        combined_file = output_path / f'{name}.combined.pem'

        if not combined_file.exists():
            with combined_file.open(mode='wb') as file:
                file.write(certs.serialize_certificate(host_cert))
                file.write(certs.serialize_certificate(ca_cert))
                file.write(certs.serialize_key(host_key))

        pfx_file = output_path / f'{name}.combined.pfx'

        if not pfx_file.exists():
            with pfx_file.open(mode='wb') as file:
                file.write(certs.serialize_pfx(name, host_key, host_cert, ca_cert))


if __name__ == '__main__':
    main()
