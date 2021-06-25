import requests
from aiohttp import (
    web,
)
from aiohttp.test_utils import (
    AioHTTPTestCase,
    unittest_run_loop,
)
from aiohttp.web_exceptions import (
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
    async def test_discovery_up_and_running(self):
        response = requests.get(
            "http://%s:%s/discover" % (self.config.discovery.connection.host, self.config.discovery.connection.port,)
        )

        self.assertEqual(200, response.status_code)

    @unittest_run_loop
    async def test_microservice_up_and_running(self):
        response = requests.get("http://localhost:5568/order/5")

        self.assertEqual(200, response.status_code)

    @unittest_run_loop
    async def test_discovery_service_call(self):
        config = MinosConfig(self.CONFIG_FILE_PATH)

        url = "/order/32"
        incoming_response = await self.client.request("GET", url)

        coordinator = MicroserviceCallCoordinator(config, incoming_response)

        result = await coordinator.call_discovery_service()
        self.assertDictEqual(
            result, {"ip": "localhost", "port": 5568, "name": "order", "status": True, "subscribed": True},
        )

    @unittest_run_loop
    async def test_discovery_raises_unavailable(self):
        config = MinosConfig(self.CONFIG_FILE_PATH)

        url = "/test-get-order/32"
        incoming_response = await self.client.request("GET", url)

        coordinator = MicroserviceCallCoordinator(config, incoming_response)

        with self.assertRaises(HTTPGatewayTimeout):
            await coordinator.call_discovery_service(host="aaa", port=self.client.port, path="/discover")

    @unittest_run_loop
    async def test_microservice_call(self):
        resp = await self.client.request("GET", "/order/5")
        assert resp.status == 200
        text = await resp.text()

        self.assertTrue("Microservice call correct!!!" in text)

    @unittest_run_loop
    async def test_microservice_raises_unavailable(self):
        config = MinosConfig(self.CONFIG_FILE_PATH)
        url = "/test-get-order/32"
        incoming_response = await self.client.request("GET", url)

        coordinator = MicroserviceCallCoordinator(config, incoming_response)
        with self.assertRaises(HTTPServiceUnavailable):
            await coordinator.call_microservice(ip="aaa", port=self.client.port)
