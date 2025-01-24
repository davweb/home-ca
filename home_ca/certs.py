"""Generate certificates and keys"""

from datetime import datetime, timezone, timedelta
from ipaddress import IPv4Address, IPv6Address
from pathlib import Path
from typing import List
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from .config import CONFIG


def generate_or_load_key(key_file: Path) -> rsa.RSAPrivateKey:
    """Generate a private key or load it from a file."""

    if key_file.exists():
        with key_file.open(mode='rb') as file:
            private_key = serialization.load_pem_private_key(file.read(), password=None)

            if not isinstance(private_key, rsa.RSAPrivateKey):
                raise ValueError('Invalid key type')

            return private_key

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    with open(key_file, 'wb') as file:
        file.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        ))

    return private_key


def generate_name(common_name: str) -> x509.Name:
    """Generate an X509 Name path for a common name"""
    return x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, CONFIG.x509_name['country']),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, CONFIG.x509_name['state']),
        x509.NameAttribute(NameOID.LOCALITY_NAME, CONFIG.x509_name['locality']),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, CONFIG.x509_name['organization']),
        x509.NameAttribute(NameOID.COMMON_NAME, common_name),
    ])


def generate_or_load_ca_certificate(certificate_file: Path, ca_key: rsa.RSAPrivateKey) -> x509.Certificate:
    """Generate a CA certificate or load it from a file."""

    if Path(certificate_file).exists():
        with certificate_file.open(mode='rb') as file:
            return x509.load_pem_x509_certificate(file.read())

    start_date = datetime.now(timezone.utc)
    # Apple limits CA validity to 825 days
    end_date = start_date + timedelta(days=CONFIG.ca_validity_days)
    subject = generate_name(f'{CONFIG.x509_name['organization']} CA')

    certificate = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        subject
    ).public_key(
        ca_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        start_date
    ).not_valid_after(
        end_date
    ).add_extension(
        x509.BasicConstraints(ca=True, path_length=None), critical=True,
    ).add_extension(
        x509.KeyUsage(
            digital_signature=True,
            content_commitment=False,
            key_encipherment=False,
            data_encipherment=False,
            key_agreement=False,
            key_cert_sign=True,
            crl_sign=True,
            encipher_only=False,
            decipher_only=False,
        ),
        critical=True,
    ).add_extension(
        x509.SubjectKeyIdentifier.from_public_key(ca_key.public_key()),
        critical=False,
    ).sign(ca_key, hashes.SHA256())

    with certificate_file.open(mode='wb') as file:
        file.write(certificate.public_bytes(serialization.Encoding.PEM))

    return certificate


def generate_or_load_server_certificate(
        certificate_file: Path,
        root_cert: x509.Certificate,
        root_key: rsa.RSAPrivateKey,
        host_key: rsa.RSAPrivateKey,
        names: List[str | IPv4Address | IPv6Address]) -> x509.Certificate:
    """Generate a Server certificate or load it from a file."""

    if Path(certificate_file).exists():
        with certificate_file.open(mode='rb') as file:
            return x509.load_pem_x509_certificate(file.read())

    start_date = datetime.now(timezone.utc)
    end_date = start_date + timedelta(days=CONFIG.server_validity_days)

    if not isinstance(names[0], str):
        raise ValueError('First name must be a string not an IP address')

    subject = generate_name(names[0])
    x509_names = [x509.DNSName(name) if isinstance(name, str) else x509.IPAddress(name) for name in names]

    host_cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        root_cert.subject
    ).public_key(
        host_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        start_date
    ).not_valid_after(
        end_date
    ).add_extension(
        x509.SubjectAlternativeName(x509_names),
        critical=False,
    ).sign(root_key, hashes.SHA256())

    with certificate_file.open(mode='wb') as file:
        file.write(host_cert.public_bytes(serialization.Encoding.PEM))

    return host_cert


def serialize_certificate(cert: x509.Certificate) -> bytes:
    """Serialize a certificate to bytes"""
    return cert.public_bytes(serialization.Encoding.PEM)
