from aiohttp import (
    web,
)

from minos.api_gateway.rest import (
    ApiGatewayConfig,
)


class Order:
    def order(self, request: web.Request, config: ApiGatewayConfig, **kwargs):
        return web.json_response(text="Order Microservice Response.")
