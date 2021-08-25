"""tests.test_api_gateway.test_rest.service module."""

import unittest
from unittest import mock
from aiohttp.test_utils import (
    AioHTTPTestCase,
    unittest_run_loop,
)
import os
import attr
from minos.api_gateway.common import MinosConfig
from minos.api_gateway.rest import ApiGatewayRestService
from tests.mock_servers.server import MockServer
from tests.utils import BASE_PATH
from aiohttp_middlewares.cors import (
    ACCESS_CONTROL_ALLOW_HEADERS,
    ACCESS_CONTROL_ALLOW_METHODS,
    ACCESS_CONTROL_ALLOW_ORIGIN,
    DEFAULT_ALLOW_HEADERS,
    DEFAULT_ALLOW_METHODS,
)


class TestApiGatewayRestService(AioHTTPTestCase):
    CONFIG_FILE_PATH = BASE_PATH / "config.yml"

    def setUp(self) -> None:
        self.config = MinosConfig(self.CONFIG_FILE_PATH)

        self.discovery = MockServer(
            host=self.config.discovery.connection.host, port=self.config.discovery.connection.port,
        )
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
            address=self.config.rest.connection.host, port=self.config.rest.connection.port, config=self.config
        )

        return await rest_service.create_application()

    @unittest_run_loop
    async def test_get(self):
        url = "/order/5?verb=GET&path=12324"
        response = await self.client.request("GET", url)

        self.assertEqual(200, response.status)
        self.assertIn("Microservice call correct!!!", await response.text())

    @unittest_run_loop
    async def test_post(self):
        url = "/order"
        response = await self.client.request("POST", url)

        self.assertEqual(200, response.status)
        self.assertIn("Microservice call correct!!!", await response.text())

    @unittest_run_loop
    async def test_put(self):
        url = "/order/5"
        response = await self.client.request("PUT", url)

        self.assertEqual(200, response.status)
        self.assertIn("Microservice call correct!!!", await response.text())

    @unittest_run_loop
    async def test_patch(self):
        url = "/order/5"
        response = await self.client.request("PATCH", url)

        self.assertEqual(200, response.status)
        self.assertIn("Microservice call correct!!!", await response.text())

    @unittest_run_loop
    async def test_delete(self):
        url = "/order/5"
        response = await self.client.request("DELETE", url)
        self.assertEqual(200, response.status)
        self.assertIn("Microservice call correct!!!", await response.text())


class TestApiGatewayRestServiceFailedDiscovery(AioHTTPTestCase):
    CONFIG_FILE_PATH = BASE_PATH / "config.yml"

    def setUp(self) -> None:
        self.config = MinosConfig(self.CONFIG_FILE_PATH)

        self.discovery = MockServer(
            host=self.config.discovery.connection.host, port=self.config.discovery.connection.port,
        )

        self.discovery.start()
        super().setUp()

    def tearDown(self) -> None:
        self.discovery.shutdown_server()
        super().tearDown()

    async def get_application(self):
        """
        Override the get_app method to return your application.
        """
        rest_service = ApiGatewayRestService(
            address=self.config.rest.connection.host, port=self.config.rest.connection.port, config=self.config
        )

        return await rest_service.create_application()

    @unittest_run_loop
    async def test_get(self):
        url = "/order/5?verb=GET&path=12324"
        response = await self.client.request("GET", url)

        self.assertEqual(502, response.status)
        self.assertIn("The discovery response is not okay.", await response.text())


class TestApiGatewayRestServiceUnreachableDiscovery(AioHTTPTestCase):
    CONFIG_FILE_PATH = BASE_PATH / "config.yml"

    def setUp(self) -> None:
        self.config = MinosConfig(self.CONFIG_FILE_PATH)
        super().setUp()

    async def get_application(self):
        """
        Override the get_app method to return your application.
        """
        rest_service = ApiGatewayRestService(
            address=self.config.rest.connection.host, port=self.config.rest.connection.port, config=self.config
        )

        return await rest_service.create_application()

    @unittest_run_loop
    async def test_get(self):
        url = "/order/5?verb=GET&path=12324"
        response = await self.client.request("GET", url)

        self.assertEqual(504, response.status)
        self.assertIn("The discovery is not available.", await response.text())


class TestApiGatewayRestServiceUnreachableMicroservice(AioHTTPTestCase):
    CONFIG_FILE_PATH = BASE_PATH / "config.yml"

    def setUp(self) -> None:
        self.config = MinosConfig(self.CONFIG_FILE_PATH)

        self.discovery = MockServer(
            host=self.config.discovery.connection.host, port=self.config.discovery.connection.port,
        )
        self.discovery.add_json_response(
            "/microservices", {"address": "localhost", "port": "5568", "status": True},
        )

        self.discovery.start()
        super().setUp()

    def tearDown(self) -> None:
        self.discovery.shutdown_server()
        super().tearDown()

    async def get_application(self):
        """
        Override the get_app method to return your application.
        """
        rest_service = ApiGatewayRestService(
            address=self.config.rest.connection.host, port=self.config.rest.connection.port, config=self.config
        )

        return await rest_service.create_application()

    @unittest_run_loop
    async def test_get(self):
        url = "/order/5?verb=GET&path=12324"
        response = await self.client.request("GET", url)

        self.assertEqual(503, response.status)
        self.assertIn("The requested endpoint is not available.", await response.text())


class TestApiGatewayCORS(AioHTTPTestCase):
    CONFIG_FILE_PATH = BASE_PATH / "config.yml"
    TEST_DENIED_ORIGIN = "https://www.google.com"
    TEST_ORIGIN = "http://localhost:3000"

    @mock.patch.dict(os.environ, {"API_GATEWAY_CORS_ENABLED": "true"})
    def setUp(self) -> None:
        self.config = MinosConfig(self.CONFIG_FILE_PATH)

        self.discovery = MockServer(
            host=self.config.discovery.connection.host, port=self.config.discovery.connection.port,
        )
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
            address=self.config.rest.connection.host, port=self.config.rest.connection.port, config=self.config
        )

        return await rest_service.create_application()

    @staticmethod
    def check_allow_origin(
        response, origin, *, allow_headers=DEFAULT_ALLOW_HEADERS, allow_methods=DEFAULT_ALLOW_METHODS,
    ):
        assert response.headers[ACCESS_CONTROL_ALLOW_ORIGIN] == origin
        if allow_headers:
            assert response.headers[ACCESS_CONTROL_ALLOW_HEADERS] == ", ".join(allow_headers)
        if allow_methods:
            assert response.headers[ACCESS_CONTROL_ALLOW_METHODS] == ", ".join(allow_methods)

    @unittest_run_loop
    async def test_cors_enabled(self):
        method = "GET"
        extra_headers = {}
        expected_origin = "*"
        expected_allow_headers = None
        expected_allow_methods = None
        url = "/order/5?verb=GET&path=12324"

        kwargs = {}
        if expected_allow_headers is not attr.NOTHING:
            kwargs["allow_headers"] = expected_allow_headers
        if expected_allow_methods is not attr.NOTHING:
            kwargs["allow_methods"] = expected_allow_methods

        self.check_allow_origin(
            await self.client.request(method, url, headers={"Origin": self.TEST_ORIGIN, **extra_headers}),
            expected_origin,
            **kwargs,
        )


if __name__ == "__main__":
    unittest.main()
