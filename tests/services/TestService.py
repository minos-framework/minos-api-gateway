from aiohttp import (
    web,
)

from minos.api_gateway.rest import (
    ApiGatewayConfig,
)


class TestService:
    def test_get_order(self, request: web.Request, config: ApiGatewayConfig, **kwargs):
        return web.json_response()
