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

        async def get_test(request):
            return web.Response(text="", status=200)

        async def microservice(request):
            return web.Response(text="", status=200)

        async def discover(request):
            if request.method == "GET":
                data = {
                    "ip": self.client.host,
                    "port": self.client.port,
                    "name": "test_endpoint",
                    "status": True,
                    "subscribed": True,
                }

            elif request.method == "POST":
                data = {
                    "ip": self.client.host,
                    "port": self.client.port,
                    "name": "microservice_post",
                    "status": True,
                    "subscribed": True,
                }
            text = json.dumps(data)
            return web.Response(text=text)

        async def post_test(request):
            return web.Response(text="", status=200)

        async def microservice_post(request):
            return web.Response(text="", status=200)

        app = web.Application()
        app.router.add_get("/get_test", get_test)
        app.router.add_get("/test_endpoint", microservice)
        app.router.add_get("/post_test", post_test)
        app.router.add_get("/microservice_post", microservice_post)
        app.router.add_get("/discover", discover)
        return app

    @unittest_run_loop
    async def test_discovery_service_call(self):
        config = MinosConfig(self.CONFIG_FILE_PATH)

        url = "/get_test"
        incoming_response = await self.client.request("GET", url)

        coordinator = MicroserviceCallCoordinator(config, incoming_response)

        success, data = await coordinator.call_discovery_service(
            host=self.client.host, port=self.client.port, path="discover", name=incoming_response.url.name
        )

        self.assertTrue(success)
        self.assertNotEqual(data, None)
        result = json.loads(data)
        self.assertDictEqual(
            result,
            {
                "ip": self.client.host,
                "port": self.client.port,
                "name": "test_endpoint",
                "status": True,
                "subscribed": True,
            },
        )

    @unittest_run_loop
    async def test_discovery_service_call_ko(self):
        config = MinosConfig(self.CONFIG_FILE_PATH)

        url = "/get_test"
        incoming_response = await self.client.request("GET", url)

        coordinator = MicroserviceCallCoordinator(config, incoming_response)

        success, data = await coordinator.call_discovery_service(
            host="aaa", port=self.client.port, path="discover", name=incoming_response.url.name
        )

        self.assertFalse(success)

    @unittest_run_loop
    async def test_microservice_call(self):
        config = MinosConfig(self.CONFIG_FILE_PATH)
        url = "/get_test"
        incoming_response = await self.client.request("GET", url)
        d = {
            "ip": self.client.host,
            "port": self.client.port,
            "name": "test_endpoint",
            "status": True,
            "subscribed": True,
        }
        coordinator = MicroserviceCallCoordinator(config, incoming_response)
        success, data = await coordinator.call_microservice(d)

        self.assertTrue(success)

    @unittest_run_loop
    async def test_microservice_call_ko(self):
        config = MinosConfig(self.CONFIG_FILE_PATH)
        url = "/get_test"
        incoming_response = await self.client.request("GET", url)
        d = {"ip": "aaa", "port": self.client.port, "name": "get_testsss", "status": True, "subscribed": True}
        coordinator = MicroserviceCallCoordinator(config, incoming_response)
        success, data = await coordinator.call_microservice(d)

        self.assertFalse(success)

    @unittest_run_loop
    async def test_orchestrator(self):
        config = MinosConfig(self.CONFIG_FILE_PATH)
        url = "/get_test"
        incoming_response = await self.client.request("GET", url)
        d = {
            "ip": self.client.host,
            "port": self.client.port,
            "name": "test_endpoint",
            "status": True,
            "subscribed": True,
        }
        coordinator = MicroserviceCallCoordinator(
            config, incoming_response, discovery_host=self.client.host, discovery_port=self.client.port
        )
        response = await coordinator.orchestrate()

        self.assertEqual(response.status, 200)

    @unittest_run_loop
    async def test_orchestrator_post(self):
        config = MinosConfig(self.CONFIG_FILE_PATH)
        url = "/post_test"
        incoming_response = await self.client.request("GET", url)
        d = {
            "ip": self.client.host,
            "port": self.client.port,
            "name": "microservice_post",
            "status": True,
            "subscribed": True,
        }
        coordinator = MicroserviceCallCoordinator(
            config, incoming_response, discovery_host=self.client.host, discovery_port=self.client.port
        )
        response = await coordinator.orchestrate()

        self.assertEqual(response.status, 200)
