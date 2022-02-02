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
from typing import (
    Any,
)

import yaml

from .exceptions import (
    ApiGatewayConfigException,
)

REST = collections.namedtuple("Rest", "host port cors auth admin")
DISCOVERY = collections.namedtuple("Discovery", "host port")
CORS = collections.namedtuple("Cors", "enabled")
AUTH_SERVICE = collections.namedtuple("AuthService", "name")
REST_ADMIN = collections.namedtuple("RestAdmin", "username password")
DATABASE = collections.namedtuple("Database", "dbname user password host port")
AUTH = collections.namedtuple("Auth", "enabled host port path services default")

_ENVIRONMENT_MAPPER = {
    "rest.host": "API_GATEWAY_REST_HOST",
    "rest.port": "API_GATEWAY_REST_PORT",
    "rest.cors.enabled": "API_GATEWAY_REST_CORS_ENABLED",
    "rest.auth.enabled": "API_GATEWAY_REST_AUTH_ENABLED",
    "rest.auth.host": "API_GATEWAY_REST_AUTH_HOST",
    "rest.auth.port": "API_GATEWAY_REST_AUTH_PORT",
    "rest.auth.path": "API_GATEWAY_REST_AUTH_PATH",
    "database.dbname": "API_GATEWAY_DATABASE_NAME",
    "database.user": "API_GATEWAY_DATABASE_USER",
    "database.password": "API_GATEWAY_DATABASE_PASSWORD",
    "database.host": "API_GATEWAY_DATABASE_HOST",
    "database.port": "API_GATEWAY_DATABASE_PORT",
    "discovery.host": "API_GATEWAY_DISCOVERY_HOST",
    "discovery.port": "API_GATEWAY_DISCOVERY_PORT",
}

_PARAMETERIZED_MAPPER = {
    "rest.host": "api_gateway_rest_host",
    "rest.port": "api_gateway_rest_port",
    "rest.cors.enabled": "api_gateway_rest_cors_enabled",
    "rest.auth.enabled": "api_gateway_rest_auth_enabled",
    "rest.auth.host": "api_gateway_rest_auth_host",
    "rest.auth.port": "api_gateway_rest_auth_port",
    "rest.auth.path": "api_gateway_rest_auth_path",
    "database.database": "api_gateway_database_name",
    "database.user": "api_gateway_database_user",
    "database.password": "api_gateway_database_password",
    "database.host": "api_gateway_database_host",
    "database.port": "api_gateway_database_port",
    "discovery.host": "api_gateway_discovery_host",
    "discovery.port": "api_gateway_discovery_port",
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
        return REST(
            host=self._get("rest.host"),
            port=int(self._get("rest.port")),
            cors=self._cors,
            auth=self._auth,
            admin=self._admin,
        )

    @property
    def _cors(self) -> CORS:
        """Get the cors config.

        :return: A ``CORS`` NamedTuple instance.
        """
        return CORS(enabled=self._get("rest.cors.enabled"))

    @property
    def _admin(self) -> REST_ADMIN:
        """Get the cors config.

        :return: A ``CORS`` NamedTuple instance.
        """
        return REST_ADMIN(username=self._get("rest.admin.username"), password=self._get("rest.admin.password"))

    @property
    def _auth(self) -> t.Optional[AUTH]:
        try:
            services = self._auth_services
            return AUTH(
                enabled=self._get("rest.auth.enabled"),
                host=self._get("rest.auth.host"),
                port=int(self._get("rest.auth.port")),
                path=self._get("rest.auth.path"),
                services=services,
                default=self._get("rest.auth.default"),
            )
        except KeyError:
            return None

    @property
    def _auth_services(self) -> list[AUTH_SERVICE]:
        info = self._get("rest.auth.services")
        services = [self._auth_service_entry(service) for service in info]
        return services

    @staticmethod
    def _auth_service_entry(service: dict[str, Any]) -> AUTH_SERVICE:
        return AUTH_SERVICE(name=service["name"],)

    @property
    def database(self) -> DATABASE:
        """Get the rest config.

        :return: A ``REST`` NamedTuple instance.
        """
        return DATABASE(
            dbname=self._get("database.dbname"),
            user=self._get("database.user"),
            password=self._get("database.password"),
            host=self._get("database.host"),
            port=int(self._get("database.port")),
        )

    @property
    def discovery(self) -> DISCOVERY:
        """Get the rest config.

        :return: A ``REST`` NamedTuple instance.
        """
        return DISCOVERY(host=self._get("discovery.host"), port=int(self._get("discovery.port")))
