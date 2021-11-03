import os
from unittest import (
    mock,
)
from uuid import (
    uuid4,
)

from aiohttp.test_utils import (
    AioHTTPTestCase,
    unittest_run_loop,
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


class TestApiGatewayAuthentication(AioHTTPTestCase):
    CONFIG_FILE_PATH = BASE_PATH / "config.yml"

    @mock.patch.dict(os.environ, {"API_GATEWAY_CORS_ENABLED": "true"})
    def setUp(self) -> None:
        self.config = ApiGatewayConfig(self.CONFIG_FILE_PATH)

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

        self.authentication_service = MockServer(host="localhost", port=8082)
        self.authentication_service.add_json_response("/token", {"sub": uuid4()}, methods=("POST",))

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
            address=self.config.rest.connection.host, port=self.config.rest.connection.port, config=self.config
        )

        return await rest_service.create_application()

    @unittest_run_loop
    async def test_auth_headers(self):
        url = "/order"
        headers = {"Authorization": "Bearer test_token"}

        response = await self.client.request("POST", url, headers=headers)

        self.assertEqual(200, response.status)
        self.assertIn("Microservice call correct!!!", await response.text())

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


class TestAuthUnreachable(AioHTTPTestCase):
    CONFIG_FILE_PATH = BASE_PATH / "config.yml"

    def setUp(self) -> None:
        self.config = ApiGatewayConfig(self.CONFIG_FILE_PATH)

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
    async def test_auth_unreachable(self):
        url = "/order"
        headers = {"Authorization": "Bearer test_token"}
        response = await self.client.request("POST", url, headers=headers)

        self.assertEqual(200, response.status)
        self.assertIn("Microservice call correct!!!", await response.text())
