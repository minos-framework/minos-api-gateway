import json

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
    MicroserviceCallCoordinator,
)
from tests.utils import (
    BASE_PATH,
)


class TestRestCoordinator(AioHTTPTestCase):
    CONFIG_FILE_PATH = BASE_PATH / "test_config.yml"

    async def get_application(self):
        """
        Override the get_app method to return your application.
        """
        app = web.Application()
        config = MinosConfig(self.CONFIG_FILE_PATH)
        rest_interface = ApiGatewayRestService(config=config, app=app)

        return await rest_interface.create_application()

    @unittest_run_loop
    async def test_discovery_service_call(self):
        config = MinosConfig(self.CONFIG_FILE_PATH)

        url = "/test-get-order/32"
        incoming_response = await self.client.request("GET", url)

        coordinator = MicroserviceCallCoordinator(config, incoming_response)

        data = await coordinator.call_discovery_service(host=self.client.host, port=self.client.port, path="discover")

        result = json.loads(data)
        self.assertDictEqual(
            result,
            {
                "ip": self.client.host,
                "port": self.client.port,
                "name": "order-microservice",
                "status": True,
                "subscribed": True,
            },
        )

    @unittest_run_loop
    async def test_discovery_service_call_ko(self):
        config = MinosConfig(self.CONFIG_FILE_PATH)

        url = "/test-get-order/32"
        incoming_response = await self.client.request("GET", url)

        coordinator = MicroserviceCallCoordinator(config, incoming_response)

        with self.assertRaises(Exception):
            await coordinator.call_discovery_service(host="aaa", port=self.client.port, path="discover")

    @unittest_run_loop
    async def test_microservice_call(self):
        config = MinosConfig(self.CONFIG_FILE_PATH)
        url = "/test-get-order/32"
        incoming_response = await self.client.request("GET", url)
        d = {
            "ip": self.client.host,
            "port": self.client.port,
            "name": "order-microservice",
            "status": True,
            "subscribed": True,
        }
        coordinator = MicroserviceCallCoordinator(config, incoming_response)
        response = await coordinator.call_microservice(d)

        self.assertEqual(response, "Order Microservice Response.")

    @unittest_run_loop
    async def test_microservice_call_ko(self):
        config = MinosConfig(self.CONFIG_FILE_PATH)
        url = "/test-get-order/32"
        incoming_response = await self.client.request("GET", url)
        d = {"ip": "aaa", "port": self.client.port, "name": "get_testsss", "status": True, "subscribed": True}

        coordinator = MicroserviceCallCoordinator(config, incoming_response)
        with self.assertRaises(Exception):
            await coordinator.call_microservice(d)

    @unittest_run_loop
    async def test_orchestrator(self):
        config = MinosConfig(self.CONFIG_FILE_PATH)
        url = "/test-get-order/32"
        incoming_response = await self.client.request("GET", url)
        coordinator = MicroserviceCallCoordinator(
            config, incoming_response, discovery_host=self.client.host, discovery_port=self.client.port
        )
        response = await coordinator.orchestrate()

        self.assertEqual(response.status, 200)

    @unittest_run_loop
    async def test_orchestrator_post(self):
        config = MinosConfig(self.CONFIG_FILE_PATH)
        url = "/test-get-order/32"
        incoming_response = await self.client.request("GET", url)
        coordinator = MicroserviceCallCoordinator(
            config, incoming_response, discovery_host=self.client.host, discovery_port=self.client.port
        )
        response = await coordinator.orchestrate()

        self.assertEqual(response.status, 200)
