import os
import unittest
from unittest import mock
from uuid import uuid4

from aiohttp.test_utils import (
    AioHTTPTestCase,
    unittest_run_loop,
)
from werkzeug.exceptions import abort

from minos.api_gateway.rest import (
    ApiGatewayConfig,
    ApiGatewayRestService,
)
from tests.mock_servers.server import MockServer
from tests.utils import BASE_PATH


class TestApiGatewayAuthentication(AioHTTPTestCase):
    CONFIG_FILE_PATH = BASE_PATH / "config.yml"

    @mock.patch.dict(os.environ, {"API_GATEWAY_REST_CORS_ENABLED": "true"})
    def setUp(self) -> None:
        self.config = ApiGatewayConfig(self.CONFIG_FILE_PATH)

        self.discovery = MockServer(host=self.config.discovery.host, port=self.config.discovery.port,)
        self.discovery.add_json_response(
            "/microservices", {"address": "localhost", "port": "5568", "status": True},
        )

        self.microservice = MockServer(host="localhost", port=5568)
        self.microservice.add_json_response(
            "/order/5", "Microservice call correct!!!", methods=("GET", "PUT", "PATCH", "DELETE",)
        )
        self.microservice.add_json_response(
            "/merchants/5", "Microservice call correct!!!", methods=("GET", "PUT", "PATCH", "DELETE",)
        )
        self.microservice.add_json_response("/categories/5", "Microservice call correct!!!", methods=("GET",))
        self.microservice.add_json_response("/order", "Microservice call correct!!!", methods=("POST",))

        self.authentication_service = MockServer(host=self.config.rest.auth.host, port=self.config.rest.auth.port)

        self.authentication_service.add_json_response("/auth/credentials", {"uuid": uuid4()}, methods=("POST",))
        self.authentication_service.add_json_response(
            "/auth/credentials/login", {"token": "credential-token-test"}, methods=("POST",)
        )
        self.authentication_service.add_json_response("/auth/credentials", {"uuid": uuid4()}, methods=("GET",))
        self.authentication_service.add_json_response(
            "/auth/token", {"uuid": uuid4(), "token": "token-test"}, methods=("POST",)
        )
        self.authentication_service.add_json_response("/auth/token/login", {"token": "token-test"}, methods=("POST",))
        self.authentication_service.add_json_response("/auth/token", {"uuid": uuid4()}, methods=("GET",))

        self.authentication_service.add_json_response("/auth/validate-token", {"uuid": uuid4()}, methods=("POST",))

        self.authentication_service.add_json_response("/auth", {"uuid": uuid4()}, methods=("POST", "GET",))

        self.discovery.start()
        self.microservice.start()
        self.authentication_service.start()
        super().setUp()

    def tearDown(self) -> None:
        self.discovery.shutdown_server()
        self.microservice.shutdown_server()
        self.authentication_service.shutdown_server()
        super().tearDown()

    async def get_application(self):
        """
        Override the get_app method to return your application.
        """
        rest_service = ApiGatewayRestService(
            address=self.config.rest.host, port=self.config.rest.port, config=self.config
        )

        return await rest_service.create_application()

    @unittest_run_loop
    async def test_auth_headers_1(self):
        url = "/order"
        headers = {"Authorization": "Bearer credential-token-test"}

        response = await self.client.request("POST", url, headers=headers)

        self.assertEqual(200, response.status)
        self.assertIn("Microservice call correct!!!", await response.text())

    @unittest_run_loop
    async def test_auth_headers_2(self):
        url = "/merchants/5"
        headers = {"Authorization": "Bearer credential-token-test"}

        response = await self.client.request("GET", url, headers=headers)

        self.assertEqual(200, response.status)
        self.assertIn("Microservice call correct!!!", await response.text())

    @unittest_run_loop
    async def test_auth_headers_3(self):
        url = "/categories/5"
        headers = {"Authorization": "Bearer credential-token-test"}

        response = await self.client.request("GET", url, headers=headers)

        self.assertEqual(200, response.status)
        self.assertIn("Microservice call correct!!!", await response.text())

    @unittest_run_loop
    async def test_default_auth_headers(self):
        url = "/auth"
        headers = {"Authorization": "Bearer credential-token-test"}

        response = await self.client.request("POST", url, headers=headers)

        self.assertEqual(200, response.status)
        self.assertIn("token", await response.text())

    @unittest_run_loop
    async def test_auth(self):
        url = "/auth/credentials"
        headers = {"Authorization": "Bearer credential-token-test"}

        response = await self.client.request("POST", url, headers=headers)

        self.assertEqual(200, response.status)
        self.assertIn("uuid", await response.text())

    @unittest_run_loop
    async def test_wrong_auth_headers(self):
        url = "/order"
        headers = {"Authorization": "Bearer"}  # Missing token
        response = await self.client.request("POST", url, headers=headers)

        self.assertEqual(200, response.status)
        self.assertIn("Microservice call correct!!!", await response.text())

    @unittest_run_loop
    async def test_request_has_token(self):
        url = "/order"
        headers = {"Authorization": "Bearer"}  # Missing token
        response = await self.client.request("POST", url, headers=headers)

        self.assertEqual(200, response.status)
        self.assertIn("Microservice call correct!!!", await response.text())


class TestAuthDisabled(AioHTTPTestCase):
    CONFIG_FILE_PATH = BASE_PATH / "config_without_auth.yml"

    def setUp(self) -> None:
        self.config = ApiGatewayConfig(self.CONFIG_FILE_PATH)

        self.discovery = MockServer(host=self.config.discovery.host, port=self.config.discovery.port,)
        self.discovery.add_json_response(
            "/microservices", {"address": "localhost", "port": "5568", "status": True},
        )

        self.microservice = MockServer(host="localhost", port=5568)
        self.microservice.add_json_response(
            "/order/5", "Microservice call correct!!!", methods=("GET", "PUT", "PATCH", "DELETE",)
        )
        self.microservice.add_json_response("/order", "Microservice call correct!!!", methods=("POST",))

        self.discovery.start()
        self.microservice.start()
        super().setUp()

    def tearDown(self) -> None:
        self.discovery.shutdown_server()
        self.microservice.shutdown_server()
        super().tearDown()

    async def get_application(self):
        """
        Override the get_app method to return your application.
        """
        rest_service = ApiGatewayRestService(
            address=self.config.rest.host, port=self.config.rest.port, config=self.config
        )

        return await rest_service.create_application()

    @unittest_run_loop
    async def test_auth_disabled(self):
        url = "/order"
        headers = {"Authorization": "Bearer test_token"}
        response = await self.client.request("POST", url, headers=headers)

        self.assertEqual(200, response.status)
        self.assertIn("Microservice call correct!!!", await response.text())


class TestAuthFailed(AioHTTPTestCase):
    CONFIG_FILE_PATH = BASE_PATH / "config.yml"

    @mock.patch.dict(os.environ, {"API_GATEWAY_REST_CORS_ENABLED": "true"})
    def setUp(self) -> None:
        self.config = ApiGatewayConfig(self.CONFIG_FILE_PATH)

        self.discovery = MockServer(host=self.config.discovery.host, port=self.config.discovery.port,)
        self.discovery.add_json_response(
            "/microservices", {"address": "localhost", "port": "5568", "status": True},
        )

        self.microservice = MockServer(host="localhost", port=5568)
        self.microservice.add_json_response(
            "/order/5", "Microservice call correct!!!", methods=("GET", "PUT", "PATCH", "DELETE",)
        )
        self.microservice.add_json_response("/order", "Microservice call correct!!!", methods=("POST",))

        self.authentication_service = MockServer(host=self.config.rest.auth.host, port=self.config.rest.auth.port)
        self.authentication_service.add_json_response("/auth/validate-token", lambda: abort(400), methods=("POST",))

        self.discovery.start()
        self.microservice.start()
        self.authentication_service.start()
        super().setUp()

    def tearDown(self) -> None:
        self.discovery.shutdown_server()
        self.microservice.shutdown_server()
        self.authentication_service.shutdown_server()
        super().tearDown()

    async def get_application(self):
        """
        Override the get_app method to return your application.
        """
        rest_service = ApiGatewayRestService(
            address=self.config.rest.host, port=self.config.rest.port, config=self.config
        )

        return await rest_service.create_application()

    @unittest_run_loop
    async def test_auth_unauthorized(self):
        url = "/merchants/jksdksdjskd"
        headers = {"Authorization": "Bearer credential-token-test_01"}

        response = await self.client.request("POST", url, headers=headers)

        self.assertEqual(401, response.status)
        self.assertIn("The given request does not have authorization to be forwarded", await response.text())


class TestAuthUnreachable(AioHTTPTestCase):
    CONFIG_FILE_PATH = BASE_PATH / "config.yml"

    def setUp(self) -> None:
        self.config = ApiGatewayConfig(self.CONFIG_FILE_PATH)

        self.discovery = MockServer(host=self.config.discovery.host, port=self.config.discovery.port,)
        self.discovery.add_json_response(
            "/microservices", {"address": "localhost", "port": "5568", "status": True},
        )

        self.microservice = MockServer(host="localhost", port=5568)
        self.microservice.add_json_response(
            "/order/5", "Microservice call correct!!!", methods=("GET", "PUT", "PATCH", "DELETE",)
        )
        self.microservice.add_json_response("/order", "Microservice call correct!!!", methods=("POST",))

        self.discovery.start()
        self.microservice.start()
        super().setUp()

    def tearDown(self) -> None:
        self.discovery.shutdown_server()
        self.microservice.shutdown_server()
        super().tearDown()

    async def get_application(self):
        """
        Override the get_app method to return your application.
        """
        rest_service = ApiGatewayRestService(
            address=self.config.rest.host, port=self.config.rest.port, config=self.config
        )

        return await rest_service.create_application()

    @unittest_run_loop
    async def test_auth_unreachable(self):
        url = "/merchants/iweuwieuwe"
        headers = {"Authorization": "Bearer test_token"}
        response = await self.client.request("POST", url, headers=headers)

        self.assertEqual(503, response.status)
        self.assertEqual("The requested endpoint is not available.", await response.text())

    @unittest_run_loop
    async def test_auth(self):
        url = "/auth/credentials"
        headers = {"Authorization": "Bearer credential-token-test"}

        response = await self.client.request("POST", url, headers=headers)

        self.assertEqual(503, response.status)
        self.assertIn("The requested endpoint is not available.", await response.text())


if __name__ == "__main__":
    unittest.main()
