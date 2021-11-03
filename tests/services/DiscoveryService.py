from aiohttp import (
    web,
)

from minos.api_gateway.rest import (
    ApiGatewayConfig,
)


class Discovery:
    def discover(self, request: web.Request, config: ApiGatewayConfig, **kwargs):
        data = {
            "ip": request.url.host,
            "port": request.url.port,
            "name": "order-microservice",
            "status": True,
            "subscribed": True,
        }
        return web.json_response(data=data)
