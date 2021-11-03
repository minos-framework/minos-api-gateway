from __future__ import (
    annotations,
)

import abc
import collections
import os
import typing as t
from distutils import (
    util,
)
from pathlib import (
    Path,
)

import yaml

from .exceptions import (
    ApiGatewayConfigException,
)

CONNECTION = collections.namedtuple("Connection", "host port")
ENDPOINT = collections.namedtuple("Endpoint", "name route method controller action")
REST = collections.namedtuple("Rest", "connection endpoints")
DISCOVERY_CONNECTION = collections.namedtuple("DiscoveryConnection", "host port path")
DATABASE = collections.namedtuple("Database", "host port password")
DISCOVERY = collections.namedtuple("Discovery", "connection endpoints database")
CORS = collections.namedtuple("Cors", "enabled")

_ENVIRONMENT_MAPPER = {
    "rest.host": "API_GATEWAY_REST_HOST",
    "rest.port": "API_GATEWAY_REST_PORT",
    "cors.enabled": "API_GATEWAY_CORS_ENABLED",
    "discovery.host": "DISCOVERY_SERVICE_HOST",
    "discovery.port": "DISCOVERY_SERVICE_PORT",
    "discovery.db.host": "DISCOVERY_SERVICE_DB_HOST",
    "discovery.db.port": "DISCOVERY_SERVICE_DB_PORT",
    "discovery.db.password": "DISCOVERY_SERVICE_DB_PASSWORD",
}

_PARAMETERIZED_MAPPER = {
    "rest.host": "api_gateway_rest_host",
    "rest.port": "api_gateway_rest_port",
    "cors.enabled": "api_gateway_cors_enabled",
    "discovery.host": "discovery_service_host",
    "discovery.port": "discovery_service_port",
    "discovery.db.host": "discovery_service_db_host",
    "discovery.db.port": "discovery_service_db_port",
    "discovery.db.password": "discovery_service_db_password",
}


class ApiGatewayConfig(abc.ABC):
    """Api Gateway config class."""

    __slots__ = ("_services", "_path", "_data", "_with_environment", "_parameterized")

    def __init__(self, path: t.Union[Path, str], with_environment: bool = True, **kwargs):
        if isinstance(path, Path):
            path = str(path)
        self._services = {}
        self._path = path
        self._load(path)
        self._with_environment = with_environment
        self._parameterized = kwargs

    @staticmethod
    def _file_exit(path: str) -> bool:
        if os.path.isfile(path):
            return True
        return False

    def _load(self, path):
        if self._file_exit(path):
            with open(path) as f:
                self._data = yaml.load(f, Loader=yaml.FullLoader)
        else:
            raise ApiGatewayConfigException(f"Check if this path: {path} is correct")

    def _get(self, key: str, **kwargs: t.Any) -> t.Any:
        if key in _PARAMETERIZED_MAPPER and _PARAMETERIZED_MAPPER[key] in self._parameterized:
            return self._parameterized[_PARAMETERIZED_MAPPER[key]]

        if self._with_environment and key in _ENVIRONMENT_MAPPER and _ENVIRONMENT_MAPPER[key] in os.environ:
            if os.environ[_ENVIRONMENT_MAPPER[key]] in ["true", "True", "false", "False"]:
                return bool(util.strtobool(os.environ[_ENVIRONMENT_MAPPER[key]]))
            return os.environ[_ENVIRONMENT_MAPPER[key]]

        def _fn(k: str, data: dict[str, t.Any]) -> t.Any:
            current, _, following = k.partition(".")

            part = data[current]
            if not following:
                return part

            return _fn(following, part)

        return _fn(key, self._data)

    @property
    def rest(self) -> REST:
        """Get the rest config.

        :return: A ``REST`` NamedTuple instance.
        """
        connection = self._rest_connection
        endpoints = self._rest_endpoints
        return REST(connection=connection, endpoints=endpoints)

    @property
    def _rest_connection(self):
        connection = CONNECTION(host=self._get("rest.host"), port=int(self._get("rest.port")))
        return connection

    @property
    def _rest_endpoints(self) -> list[ENDPOINT]:
        info = self._get("rest.endpoints")
        endpoints = [self._rest_endpoints_entry(endpoint) for endpoint in info]
        return endpoints

    @staticmethod
    def _rest_endpoints_entry(endpoint: dict[str, t.Any]) -> ENDPOINT:
        return ENDPOINT(
            name=endpoint["name"],
            route=endpoint["route"],
            method=endpoint["method"].upper(),
            controller=endpoint["controller"],
            action=endpoint["action"],
        )

    @property
    def cors(self) -> CORS:
        """Get the cors config.

        :return: A ``CORS`` NamedTuple instance.
        """
        return CORS(enabled=self._get("cors.enabled"))

    @property
    def discovery(self) -> DISCOVERY:
        """Get the rest config.

        :return: A ``REST`` NamedTuple instance.
        """
        connection = self._discovery_connection
        endpoints = self._discovery_endpoints
        database = self._discovery_database
        return DISCOVERY(connection=connection, endpoints=endpoints, database=database)

    @property
    def _discovery_connection(self):
        connection = DISCOVERY_CONNECTION(
            host=self._get("discovery.host"), port=int(self._get("discovery.port")), path=self._get("discovery.path")
        )
        return connection

    @property
    def _discovery_database(self):
        connection = DATABASE(
            host=self._get("discovery.db.host"),
            port=int(self._get("discovery.db.port")),
            password=self._get("discovery.db.password"),
        )
        return connection

    @property
    def _discovery_endpoints(self) -> list[ENDPOINT]:
        info = self._get("discovery.endpoints")
        endpoints = [self._discovery_endpoints_entry(endpoint) for endpoint in info]
        return endpoints

    @staticmethod
    def _discovery_endpoints_entry(endpoint: dict[str, t.Any]) -> ENDPOINT:
        return ENDPOINT(
            name=endpoint["name"],
            route=endpoint["route"],
            method=endpoint["method"].upper(),
            controller=endpoint["controller"],
            action=endpoint["action"],
        )
