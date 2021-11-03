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

REST = collections.namedtuple("Rest", "host port cors")
DISCOVERY = collections.namedtuple("Discovery", "host port")
CORS = collections.namedtuple("Cors", "enabled")

_ENVIRONMENT_MAPPER = {
    "rest.host": "API_GATEWAY_REST_HOST",
    "rest.port": "API_GATEWAY_REST_PORT",
    "rest.cors.enabled": "API_GATEWAY_REST_CORS_ENABLED",
    "discovery.host": "DISCOVERY_SERVICE_HOST",
    "discovery.port": "DISCOVERY_SERVICE_PORT",
}

_PARAMETERIZED_MAPPER = {
    "rest.host": "api_gateway_rest_host",
    "rest.port": "api_gateway_rest_port",
    "rest.cors.enabled": "api_gateway_rest_cors_enabled",
    "discovery.host": "discovery_service_host",
    "discovery.port": "discovery_service_port",
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
        return REST(host=self._get("rest.host"), port=int(self._get("rest.port")), cors=self._cors)

    @property
    def _cors(self) -> CORS:
        """Get the cors config.

        :return: A ``CORS`` NamedTuple instance.
        """
        return CORS(enabled=self._get("rest.cors.enabled"))

    @property
    def discovery(self) -> DISCOVERY:
        """Get the rest config.

        :return: A ``REST`` NamedTuple instance.
        """
        return DISCOVERY(host=self._get("discovery.host"), port=int(self._get("discovery.port")))
