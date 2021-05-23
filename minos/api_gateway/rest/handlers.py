from aiohttp import (
    web,
)

from minos.api_gateway.common import (
    MinosConfig,
)
from minos.api_gateway.rest import (
    MicroserviceCallCoordinator,
)


class ApiGatewayHandler(object):
    async def get_order(self, request: web.Request, config: MinosConfig, **kwargs):
        coordinator = MicroserviceCallCoordinator(config, request, request.url.host, request.url.port)
        response = await coordinator.orchestrate()
        return response

    async def post_order(self, request: web.Request, config: MinosConfig, **kwargs):
        coordinator = MicroserviceCallCoordinator(config, request, request.url.host, request.url.port)
        response = await coordinator.orchestrate()
        return response

    async def put_order(self, request: web.Request, config: MinosConfig, **kwargs):
        coordinator = MicroserviceCallCoordinator(config, request, request.url.host, request.url.port)
        response = await coordinator.orchestrate()
        return response

    async def patch_order(self, request: web.Request, config: MinosConfig, **kwargs):
        coordinator = MicroserviceCallCoordinator(config, request, request.url.host, request.url.port)
        response = await coordinator.orchestrate()
        return response

    async def delete_order(self, request: web.Request, config: MinosConfig, **kwargs):
        coordinator = MicroserviceCallCoordinator(config, request, request.url.host, request.url.port)
        response = await coordinator.orchestrate()
        return response
