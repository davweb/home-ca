
"""Load configuration from the command line and config files"""

import argparse
from collections import namedtuple
from pathlib import Path
from typing import Any, Dict, List
import sys
import yaml

Host = namedtuple('Host', ['names', 'ip_addresses'], defaults=[[]])


def _get_arguments(default_config_file) -> argparse.Namespace:
    """Parse command line arguments"""

    parser = argparse.ArgumentParser(description='Generate certificates for Home Network')
    parser.add_argument('-o', '--output-directory', type=str, help='Output directory for certificates and keys')
    parser.add_argument('-f', '--config-file', type=str, default=default_config_file, help='Configuration file')

    return parser.parse_args()


def _parse_config(config_file) -> Dict[str, Any]:
    """Parse the YAML config file"""

    try:
        with open(config_file, 'r', encoding='UTF-8') as stream:
            try:
                return yaml.load(stream, Loader=yaml.BaseLoader)
            except yaml.YAMLError as exc:
                print(f'An error occurred while parsing the YAML file: {exc}', file=sys.stderr)
                sys.exit(1)
    except FileNotFoundError:
        return {}


class Config:
    """Configuration class"""

    def __init__(self) -> None:
        self._args = _get_arguments(default_config_file=self.base_dir / 'config.yaml')
        self._config_file_name = self._args.config_file
        self._file = _parse_config(self.config_file)

    @property
    def config_file(self) -> str:
        """Return the name of the config file"""
        return self._config_file_name

    @property
    def base_dir(self) -> Path:
        """Return the base directory of the script"""
        return Path(__file__).parent.parent

    @property
    def output_path(self) -> Path:
        """Output directory path is from the command line or the config file or else certs"""

        if self._args.output_directory:
            return Path(self._args.output_directory)

        return Path(self._file.get('output_directory', 'certificates'))

    @property
    def x509_name(self) -> Dict[str, str]:
        """Return the x509 name from the config file"""

        name = self._file.get('name')

        if not name:
            raise ValueError('No x509 name defined in the config file')

        return name

    @property
    def domain(self) -> str:
        """Return the domain name from the config file or local"""

        return self._file.get('domain', 'local')

    @property
    def hosts(self) -> List[Host]:
        """Return the hosts from the config file"""

        if 'hosts' not in self._file:
            raise ValueError('No hosts defined in the config file')

        return [Host(**host) for host in self._file.get('hosts', [])]

    @property
    def ca_validity_days(self) -> int:
        """Return the CA certificate validity in days"""

        # Apple limits internal CA validity to 825 days
        return 825

    @property
    def server_validity_days(self) -> int:
        """Return the CA certificate validity in days"""

        # Maximum validity for a server certificate is 398 days
        return 398


CONFIG = Config()
