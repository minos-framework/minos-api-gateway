"""
Copyright (C) 2021 Clariteia SL

This file is part of minos framework.

Minos framework can not be copied and/or distributed without the express permission of Clariteia SL.
"""
import os
import unittest
from unittest import (
    mock,
)

from minos.api_gateway.rest import (
    ApiGatewayConfig,
    ApiGatewayConfigException,
)
from tests.utils import (
    BASE_PATH,
)


class TestApiGatewayConfig(unittest.TestCase):
    def setUp(self) -> None:
        self.config_file_path = BASE_PATH / "config.yml"

    def test_config_ini_fail(self):
        with self.assertRaises(ApiGatewayConfigException):
            ApiGatewayConfig(path=BASE_PATH / "test_fail_config.yaml")

    def test_config_rest(self):
        config = ApiGatewayConfig(path=self.config_file_path)
        rest = config.rest

        self.assertEqual("localhost", rest.host)
        self.assertEqual(5566, rest.port)

    def test_config_rest_cors(self):
        config = ApiGatewayConfig(path=self.config_file_path)
        cors = config.rest.cors

        self.assertEqual(True, cors.enabled)

    def test_config_rest_auth(self):
        config = ApiGatewayConfig(path=self.config_file_path)
        auth = config.rest.auth

        self.assertEqual(True, auth.enabled)
        self.assertEqual("localhost", auth.host)
        self.assertEqual(55909, auth.port)
        self.assertEqual("POST", auth.method)
        self.assertEqual("/auth/validate-token", auth.path)

    def test_config_rest_auth_none(self):
        config = ApiGatewayConfig(path=BASE_PATH / "config_without_auth.yml")
        self.assertIsNone(config.rest.auth)

    def test_config_discovery(self):
        config = ApiGatewayConfig(path=self.config_file_path)
        discovery = config.discovery

        self.assertEqual("localhost", discovery.host)
        self.assertEqual(5567, discovery.port)

    @mock.patch.dict(os.environ, {"API_GATEWAY_DISCOVERY_HOST": "::1"})
    def test_overwrite_with_environment_discovery_host(self):
        config = ApiGatewayConfig(path=self.config_file_path)
        self.assertEqual("::1", config.discovery.host)

    @mock.patch.dict(os.environ, {"API_GATEWAY_DISCOVERY_PORT": "4040"})
    def test_overwrite_with_environment_discovery_port(self):
        config = ApiGatewayConfig(path=self.config_file_path)
        self.assertEqual(4040, config.discovery.port)

    @mock.patch.dict(os.environ, {"API_GATEWAY_REST_HOST": "::1"})
    def test_overwrite_with_environment(self):
        config = ApiGatewayConfig(path=self.config_file_path)
        rest = config.rest
        self.assertEqual("::1", rest.host)

    @mock.patch.dict(os.environ, {"API_GATEWAY_REST_HOST": "::1"})
    def test_overwrite_with_environment_false(self):
        config = ApiGatewayConfig(path=self.config_file_path, with_environment=False)
        rest = config.rest
        self.assertEqual("localhost", rest.host)

    @mock.patch.dict(os.environ, {"API_GATEWAY_REST_CORS_ENABLED": "false"})
    def test_overwrite_with_environment_cors(self):
        config = ApiGatewayConfig(path=self.config_file_path)
        cors = config.rest.cors

        self.assertEqual(False, cors.enabled)

    @mock.patch.dict(os.environ, {"API_GATEWAY_REST_AUTH_ENABLED": "false"})
    def test_overwrite_with_environment_rest_auth_enabled(self):
        config = ApiGatewayConfig(path=self.config_file_path)
        auth = config.rest.auth

        self.assertEqual(False, auth.enabled)

    @mock.patch.dict(os.environ, {"API_GATEWAY_REST_AUTH_HOST": "auth"})
    def test_overwrite_with_environment_rest_auth_host(self):
        config = ApiGatewayConfig(path=self.config_file_path)
        auth = config.rest.auth

        self.assertEqual("auth", auth.host)

    @mock.patch.dict(os.environ, {"API_GATEWAY_REST_AUTH_PORT": "9999"})
    def test_overwrite_with_environment_rest_auth_port(self):
        config = ApiGatewayConfig(path=self.config_file_path)
        auth = config.rest.auth

        self.assertEqual(9999, auth.port)

    @mock.patch.dict(os.environ, {"API_GATEWAY_REST_AUTH_METHOD": "GET"})
    def test_overwrite_with_environment_rest_auth_method(self):
        config = ApiGatewayConfig(path=self.config_file_path)
        auth = config.rest.auth

        self.assertEqual("GET", auth.method)

    @mock.patch.dict(os.environ, {"API_GATEWAY_REST_AUTH_PATH": "/auth"})
    def test_overwrite_with_environment_rest_auth_path(self):
        config = ApiGatewayConfig(path=self.config_file_path)
        auth = config.rest.auth

        self.assertEqual("/auth", auth.path)

    def test_overwrite_with_parameter(self):
        config = ApiGatewayConfig(path=self.config_file_path, api_gateway_rest_host="::1")
        rest = config.rest
        self.assertEqual("::1", rest.host)

    def test_overwrite_with_parameter_rest_cors(self):
        config = ApiGatewayConfig(path=self.config_file_path, api_gateway_rest_cors_enabled=False)
        cors = config.rest.cors
        self.assertEqual(False, cors.enabled)

    def test_overwrite_with_parameter_rest_auth_enabled(self):
        config = ApiGatewayConfig(path=self.config_file_path, api_gateway_rest_auth_enabled=False)
        auth = config.rest.auth
        self.assertEqual(False, auth.enabled)

    def test_overwrite_with_parameter_rest_auth_host(self):
        config = ApiGatewayConfig(path=self.config_file_path, api_gateway_rest_auth_host="auth")
        auth = config.rest.auth

        self.assertEqual("auth", auth.host)

    def test_overwrite_with_parameter_rest_auth_port(self):
        config = ApiGatewayConfig(path=self.config_file_path, api_gateway_rest_auth_port="9999")
        auth = config.rest.auth

        self.assertEqual(9999, auth.port)

    def test_overwrite_with_parameter_rest_auth_method(self):
        config = ApiGatewayConfig(path=self.config_file_path, api_gateway_rest_auth_method="GET")
        auth = config.rest.auth

        self.assertEqual("GET", auth.method)

    def test_overwrite_with_parameter_rest_auth_path(self):
        config = ApiGatewayConfig(path=self.config_file_path, api_gateway_rest_auth_path="/auth")
        auth = config.rest.auth

        self.assertEqual("/auth", auth.path)


if __name__ == "__main__":
    unittest.main()
