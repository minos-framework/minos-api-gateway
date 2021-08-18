import asyncio
import logging

from aiohttp import web
from aiomisc.service.aiohttp import AIOHTTPService

from minos.api_gateway.common import MinosConfig
from minos.api_gateway.rest import handler

logger = logging.getLogger(__name__)


class ApiGatewayRestService(AIOHTTPService):
    def __init__(self, address: str, port: int, config: MinosConfig, graceful_stop_timeout: int = 5):
        self.config = config
        self.graceful_stop_timeout = graceful_stop_timeout
        super().__init__(address, port)

    async def create_application(self) -> web.Application:
        app = web.Application()
        app["config"] = self.config

        app.router.add_route("*", "/{endpoint:.*}", handler.orchestrate)

        return app

    async def stop(self, exception: Exception = None) -> None:
        logger.info(
            f"Stopping Discovery Service gracefully "
            f"(waiting {self.graceful_stop_timeout} seconds for microservices unsubscription)..."
        )
        await asyncio.sleep(self.graceful_stop_timeout)
        await super().stop(exception)
