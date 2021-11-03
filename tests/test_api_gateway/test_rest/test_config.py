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

        broker = rest.connection
        self.assertEqual("localhost", broker.host)
        self.assertEqual(55909, broker.port)

    def test_config_discovery(self):
        config = ApiGatewayConfig(path=self.config_file_path)
        discovery = config.discovery

        conn = discovery.connection
        self.assertEqual("localhost", conn.host)
        self.assertEqual(5567, conn.port)

        db = discovery.database
        self.assertEqual("localhost", db.host)
        self.assertEqual(6379, db.port)
        self.assertEqual(None, db.password)

        self.assertEqual("", discovery.connection.path)

    def test_config_cors(self):
        config = ApiGatewayConfig(path=self.config_file_path)
        cors = config.cors

        self.assertIsInstance(cors.enabled, bool)
        self.assertFalse(cors.enabled)

    @mock.patch.dict(os.environ, {"DISCOVERY_SERVICE_HOST": "::1"})
    def test_overwrite_with_environment_discovery_host(self):
        config = ApiGatewayConfig(path=self.config_file_path)
        conn = config.discovery.connection
        self.assertEqual("::1", conn.host)

    @mock.patch.dict(os.environ, {"DISCOVERY_SERVICE_PORT": "4040"})
    def test_overwrite_with_environment_discovery_port(self):
        config = ApiGatewayConfig(path=self.config_file_path)
        conn = config.discovery.connection
        self.assertEqual(4040, conn.port)

    @mock.patch.dict(os.environ, {"DISCOVERY_SERVICE_DB_HOST": "::1"})
    def test_overwrite_with_environment_discovery_db_host(self):
        config = ApiGatewayConfig(path=self.config_file_path)
        conn = config.discovery.database
        self.assertEqual("::1", conn.host)

    @mock.patch.dict(os.environ, {"DISCOVERY_SERVICE_DB_PORT": "3030"})
    def test_overwrite_with_environment_discovery_db_port(self):
        config = ApiGatewayConfig(path=self.config_file_path)
        conn = config.discovery.database
        self.assertEqual(3030, conn.port)

    @mock.patch.dict(os.environ, {"DISCOVERY_SERVICE_DB_PASSWORD": "1234"})
    def test_overwrite_with_environment_discovery_db_password(self):
        config = ApiGatewayConfig(path=self.config_file_path)
        conn = config.discovery.database
        self.assertEqual("1234", conn.password)

    @mock.patch.dict(os.environ, {"API_GATEWAY_REST_HOST": "::1"})
    def test_overwrite_with_environment(self):
        config = ApiGatewayConfig(path=self.config_file_path)
        rest = config.rest
        self.assertEqual("::1", rest.connection.host)

    @mock.patch.dict(os.environ, {"API_GATEWAY_REST_HOST": "::1"})
    def test_overwrite_with_environment_false(self):
        config = ApiGatewayConfig(path=self.config_file_path, with_environment=False)
        rest = config.rest
        self.assertEqual("localhost", rest.connection.host)

    @mock.patch.dict(os.environ, {"API_GATEWAY_CORS_ENABLED": "false"})
    def test_overwrite_with_environment_cors(self):
        config = ApiGatewayConfig(path=self.config_file_path)
        cors = config.cors

        self.assertIsInstance(cors.enabled, bool)
        self.assertFalse(cors.enabled)

    def test_overwrite_with_parameter(self):
        config = ApiGatewayConfig(path=self.config_file_path, api_gateway_rest_host="::1")
        rest = config.rest
        self.assertEqual("::1", rest.connection.host)

    def test_overwrite_with_parameter_cors(self):
        config = ApiGatewayConfig(path=self.config_file_path, api_gateway_cors_enabled=False)
        cors = config.cors

        self.assertIsInstance(cors.enabled, bool)
        self.assertFalse(cors.enabled)


if __name__ == "__main__":
    unittest.main()
