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
from tests.utils import (
    BASE_PATH,
)


class TestRestService(AioHTTPTestCase):
    CONFIG_FILE_PATH = BASE_PATH / "config.yml"

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
        url = "/discover"
        resp = await self.client.request("GET", url)
        assert resp.status == 200
        # text = await resp.text()

    @unittest_run_loop
    async def test_get(self):
        url = "/order/3"
        resp = await self.client.request("GET", url)
        assert resp.status == 200

    @unittest_run_loop
    async def test_post(self):
        url = "/order"
        resp = await self.client.request("POST", url)
        assert resp.status == 200

    @unittest_run_loop
    async def test_put(self):
        url = "/order/34"
        resp = await self.client.request("PUT", url)
        assert resp.status == 200

    @unittest_run_loop
    async def test_patch(self):
        url = "/order/34"
        resp = await self.client.request("PATCH", url)
        assert resp.status == 200

    @unittest_run_loop
    async def test_delete(self):
        url = "/order/34"
        resp = await self.client.request("DELETE", url)
        assert resp.status == 200
