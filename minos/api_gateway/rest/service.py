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

from .config import (
    ApiGatewayConfig,
)
from .handler import (
    AdminHandler,
    authentication,
    authentication_default,
    orchestrate,
)

logger = logging.getLogger(__name__)


class ApiGatewayRestService(AIOHTTPService):
    def __init__(self, address: str, port: int, config: ApiGatewayConfig):
        self.config = config
        super().__init__(address, port)

    async def create_application(self) -> web.Application:
        middlewares = list()
        if self.config.rest.cors.enabled:
            middlewares = [cors_middleware(allow_all=True)]

        app = web.Application(middlewares=middlewares)

        app["config"] = self.config

        auth = self.config.rest.auth
        if auth is not None and auth.enabled:
            app.router.add_route("*", "/auth", authentication_default)
            for service in auth.services:
                app.router.add_route("*", f"/auth/{service.name}", authentication)

        app.router.add_route("POST", "/admin/login", AdminHandler.login)
        app.router.add_route("*", "/{endpoint:.*}", orchestrate)

        return app
