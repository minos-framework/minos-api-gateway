import requests
from aiohttp import (
    web,
)
from aiohttp.test_utils import (
    AioHTTPTestCase,
    unittest_run_loop,
)

from minos.api_gateway.common import (
    MinosConfig,
)
from minos.api_gateway.rest import (
    ApiGatewayRestService,
)
from tests.mock_servers.server import (
    MockServer,
)
from tests.utils import (
    BASE_PATH,
)


class TestRestService(AioHTTPTestCase):
    CONFIG_FILE_PATH = BASE_PATH / "config.yml"

    def setUp(self) -> None:
        self.config = MinosConfig(self.CONFIG_FILE_PATH)
        self.discovery_server = MockServer(
            host=self.config.discovery.connection.host, port=self.config.discovery.connection.port,
        )
        self.discovery_server.add_json_response(
            "/discover", {"ip": "localhost", "port": "5568", "status": True}, methods=("GET",),
        )

        self.order_microservice = MockServer(host="localhost", port=5568)
        self.order_microservice.add_json_response(
            "/order/5", "Microservice call correct!!!", methods=("GET", "PUT", "PATCH", "DELETE",)
        )
        self.order_microservice.add_json_response("/order", "Microservice call correct!!!", methods=("POST",))

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
        config = MinosConfig(self.CONFIG_FILE_PATH)
        rest_interface = ApiGatewayRestService(
            address=config.rest.connection.host, port=config.rest.connection.port, config=config
        )

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
    async def test_get(self):
        url = "/order/5?verb=GET&path=12324"
        resp = await self.client.request("GET", url)
        assert resp.status == 200
        text = await resp.text()
        self.assertTrue("Microservice call correct!!!" in text)

    @unittest_run_loop
    async def test_post(self):
        url = "/order"
        resp = await self.client.request("POST", url)
        assert resp.status == 200
        text = await resp.text()
        self.assertTrue("Microservice call correct!!!" in text)

    @unittest_run_loop
    async def test_put(self):
        url = "/order/5"
        resp = await self.client.request("PUT", url)
        assert resp.status == 200
        text = await resp.text()
        self.assertTrue("Microservice call correct!!!" in text)

    @unittest_run_loop
    async def test_patch(self):
        url = "/order/5"
        resp = await self.client.request("PATCH", url)
        assert resp.status == 200
        text = await resp.text()
        self.assertTrue("Microservice call correct!!!" in text)

    @unittest_run_loop
    async def test_delete(self):
        url = "/order/5"
        resp = await self.client.request("DELETE", url)
        assert resp.status == 200
        text = await resp.text()
        self.assertTrue("Microservice call correct!!!" in text)
