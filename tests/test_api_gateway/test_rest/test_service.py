"""tests.test_api_gateway.test_rest.service module."""

import os
import unittest

from aiohttp.test_utils import (
    AioHTTPTestCase,
    unittest_run_loop,
)
from werkzeug.exceptions import (
    abort,
)

from minos.api_gateway.rest import (
    ApiGatewayConfig,
    ApiGatewayRestService,
)
from tests.mock_servers.server import (
    MockServer,
)
from tests.utils import (
    BASE_PATH,
)


class TestApiGatewayRestService(AioHTTPTestCase):
    CONFIG_FILE_PATH = BASE_PATH / "config.yml"

    def setUp(self) -> None:
        os.environ["API_GATEWAY_REST_AUTH_ENABLED"] = "false"
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


class TestApiGatewayRestServiceNotFoundDiscovery(AioHTTPTestCase):
    CONFIG_FILE_PATH = BASE_PATH / "config.yml"

    def setUp(self) -> None:
        self.config = ApiGatewayConfig(self.CONFIG_FILE_PATH)

        self.discovery = MockServer(host=self.config.discovery.host, port=self.config.discovery.port,)

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
            address=self.config.rest.host, port=self.config.rest.port, config=self.config
        )

        return await rest_service.create_application()

    @unittest_run_loop
    async def test_get(self):
        url = "/order/5?verb=GET&path=12324"
        response = await self.client.request("GET", url)

        self.assertEqual(404, response.status)
        self.assertIn("The '/order/5' path is not available for 'GET' method.", await response.text())


class TestApiGatewayRestServiceFailedDiscovery(AioHTTPTestCase):
    CONFIG_FILE_PATH = BASE_PATH / "config.yml"

    def setUp(self) -> None:
        self.config = ApiGatewayConfig(self.CONFIG_FILE_PATH)

        self.discovery = MockServer(host=self.config.discovery.host, port=self.config.discovery.port,)
        self.discovery.add_callback_response("/microservices", lambda: abort(400), methods=("GET",))

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
            address=self.config.rest.host, port=self.config.rest.port, config=self.config
        )

        return await rest_service.create_application()

    @unittest_run_loop
    async def test_get(self):
        url = "/order/5?verb=GET&path=12324"
        response = await self.client.request("GET", url)

        self.assertEqual(502, response.status)
        self.assertIn("The Discovery Service response is wrong.", await response.text())


class TestApiGatewayRestServiceUnreachableDiscovery(AioHTTPTestCase):
    CONFIG_FILE_PATH = BASE_PATH / "config.yml"

    def setUp(self) -> None:
        os.environ["API_GATEWAY_REST_AUTH_ENABLED"] = "false"
        self.config = ApiGatewayConfig(self.CONFIG_FILE_PATH)
        super().setUp()

    async def get_application(self):
        """
        Override the get_app method to return your application.
        """
        rest_service = ApiGatewayRestService(
            address=self.config.rest.host, port=self.config.rest.port, config=self.config
        )

        return await rest_service.create_application()

    @unittest_run_loop
    async def test_get(self):
        url = "/order/5?verb=GET&path=12324"
        response = await self.client.request("GET", url)

        self.assertEqual(504, response.status)
        self.assertIn("The Discovery Service is not available.", await response.text())


class TestApiGatewayRestServiceUnreachableMicroservice(AioHTTPTestCase):
    CONFIG_FILE_PATH = BASE_PATH / "config.yml"

    def setUp(self) -> None:
        self.config = ApiGatewayConfig(self.CONFIG_FILE_PATH)

        self.discovery = MockServer(host=self.config.discovery.host, port=self.config.discovery.port,)
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
            address=self.config.rest.host, port=self.config.rest.port, config=self.config
        )

        return await rest_service.create_application()

    @unittest_run_loop
    async def test_get(self):
        url = "/order/5?verb=GET&path=12324"
        response = await self.client.request("GET", url)

        self.assertEqual(503, response.status)
        self.assertIn("The requested endpoint is not available.", await response.text())


if __name__ == "__main__":
    unittest.main()
