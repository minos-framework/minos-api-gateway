from aiohttp import (
    web,
)

from minos.api_gateway.common import (
    MinosConfig,
)


class Order:
    def order(self, request: web.Request, config: MinosConfig, **kwargs):
        return web.json_response(text="Order Microservice Response.")
