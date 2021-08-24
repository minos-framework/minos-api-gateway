"""minos.api_gateway.rest.service module."""

import logging

from aiohttp import (
    web,
)
from aiohttp_middlewares import (
    cors_middleware,
)
from aiomisc.service.aiohttp import (
    AIOHTTPService,
)

from minos.api_gateway.common import (
    MinosConfig,
)
from minos.api_gateway.rest import (
    handler,
)

logger = logging.getLogger(__name__)


class ApiGatewayRestService(AIOHTTPService):
    def __init__(self, address: str, port: int, config: MinosConfig):
        self.config = config
        super().__init__(address, port)

    async def create_application(self) -> web.Application:
        app = web.Application(middlewares=[cors_middleware(allow_all=True)])
        app["config"] = self.config

        app.router.add_route("*", "/{endpoint:.*}", handler.orchestrate)

        return app
