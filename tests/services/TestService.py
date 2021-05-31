from aiohttp import (
    web,
)

from minos.api_gateway.common import (
    MinosConfig,
)


class TestService:
    def test_get_order(self, request: web.Request, config: MinosConfig, **kwargs):
        return web.json_response()
