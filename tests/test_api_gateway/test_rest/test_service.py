"""tests.test_api_gateway.test_rest.service module."""

import unittest

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


if __name__ == "__main__":
    unittest.main()
