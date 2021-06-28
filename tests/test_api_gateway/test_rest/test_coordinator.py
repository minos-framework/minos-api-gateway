import unittest
from unittest.mock import (
    patch,
)

from aiohttp import (
    web,
)
from aiohttp.test_utils import (
    AioHTTPTestCase,
    unittest_run_loop,
)
from aiohttp.web_exceptions import (
    HTTPBadGateway,
    HTTPGatewayTimeout,
    HTTPServiceUnavailable,
)

from minos.api_gateway.common import (
    MinosConfig,
)
from minos.api_gateway.rest import (
    ApiGatewayRestService,
    MicroserviceCallCoordinator,
)
from tests.mock_servers.server import (
    MockServer,
)
from tests.utils import (
    BASE_PATH,
)


class _FakeResponse:
    """For testing purposes."""

    def __init__(self, ok: bool = True, json=None):
        self.ok = ok
        self._json = json

    async def json(self):
        """For testing purposes."""
        return self._json

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def __aenter__(self):
        return self


class TestRestCoordinator(AioHTTPTestCase):
    CONFIG_FILE_PATH = BASE_PATH / "config.yml"

    def setUp(self) -> None:
        self.config = MinosConfig(self.CONFIG_FILE_PATH)
        self.discovery_server = MockServer(
            host=self.config.discovery.connection.host, port=self.config.discovery.connection.port,
        )
        self.discovery_server.add_json_response(
            "/discover",
            {"ip": "localhost", "port": "5568", "name": "order", "status": True, "subscribed": True},
            methods=("GET",),
        )

        self.order_microservice = MockServer(host="localhost", port=5568)
        self.order_microservice.add_json_response(
            "/order/5", "Microservice call correct!!!", methods=("GET", "PUT", "POST", "PATCH", "DELETE")
        )

        self.discovery_server.start()
        self.order_microservice.start()

        self.config = MinosConfig(self.CONFIG_FILE_PATH)
        super().setUp()

    def tearDown(self) -> None:
        self.discovery_server.shutdown_server()
        self.order_microservice.shutdown_server()
        super().tearDown()

    async def get_application(self):
        """
        Override the get_app method to return your application.
        """
        app = web.Application()
        config = MinosConfig(self.CONFIG_FILE_PATH)
        rest_interface = ApiGatewayRestService(config=config, app=app)

        return await rest_interface.create_application()

    @unittest_run_loop
    async def test_discover(self):
        url = "/order/32"
        incoming_response = await self.client.request("GET", url)

        coordinator = MicroserviceCallCoordinator(self.config, incoming_response)

        result = await coordinator.discover()
        self.assertDictEqual(
            result, {"ip": "localhost", "port": 5568, "name": "order", "status": True, "subscribed": True},
        )

    @unittest_run_loop
    async def test_discover_raises_unavailable(self):
        url = "/test-get-order/32"
        incoming_response = await self.client.request("GET", url)

        coordinator = MicroserviceCallCoordinator(self.config, incoming_response)

        with self.assertRaises(HTTPGatewayTimeout):
            await coordinator.discover(host="aaa", port=self.client.port, path="/discover")

    @unittest_run_loop
    async def test_discover_raises_bad_response(self):
        incoming_response = await self.client.request("GET", "/fake/32")

        coordinator = MicroserviceCallCoordinator(self.config, incoming_response)
        with patch("aiohttp.ClientSession.get", return_value=_FakeResponse(ok=False)):
            with self.assertRaises(HTTPBadGateway):
                await coordinator.discover()

    @unittest_run_loop
    async def test_discover_raises_unavailable_microservice(self):
        incoming_response = await self.client.request("GET", "/fake/32")

        coordinator = MicroserviceCallCoordinator(self.config, incoming_response)
        with patch("aiohttp.ClientSession.get", return_value=_FakeResponse(json={"status": False})):
            with self.assertRaises(HTTPServiceUnavailable):
                await coordinator.discover()

    @unittest_run_loop
    async def test_call_raises_unavailable(self):
        url = "/test-get-order/32"
        incoming_response = await self.client.request("GET", url)

        coordinator = MicroserviceCallCoordinator(self.config, incoming_response)
        with self.assertRaises(HTTPServiceUnavailable):
            await coordinator.call(ip="aaa", port=self.client.port)


if __name__ == "__main__":
    unittest.main()
