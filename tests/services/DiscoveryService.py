from aiohttp import (
    web,
)

from minos.api_gateway.common import (
    MinosConfig,
)


class Discovery:
    def discover(self, request: web.Request, config: MinosConfig, **kwargs):
        data = {
            "ip": request.url.host,
            "port": request.url.port,
            "name": "order-microservice",
            "status": True,
            "subscribed": True,
        }
        return web.json_response(data=data)
