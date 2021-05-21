import json

from aiohttp import (
    web,
)
from minos.api_gateway.rest import MicroserviceCallCoordinator
from minos.api_gateway.common import (
    MinosConfig,
)



class ApiGatewayHandler(object):
    async def get_order(self, request: web.Request, config: MinosConfig, **kwargs):
        response = MicroserviceCallCoordinator(config, request)
        return response

    async def post_order(self, request: web.Request, config: MinosConfig, **kwargs):
        response = MicroserviceCallCoordinator(config, request)
        return response

    async def put_order(self, request: web.Request, config: MinosConfig, **kwargs):
        return web.Response(text="Order added", status=200)

    async def patch_order(self, request: web.Request, config: MinosConfig, **kwargs):
        return web.Response(text="Order added", status=200)

    async def delete_order(self, request: web.Request, config: MinosConfig, **kwargs):
        return web.Response(text="Order added", status=200)
