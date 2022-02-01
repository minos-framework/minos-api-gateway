import logging

from aiohttp import web
from aiohttp_middlewares import cors_middleware
from aiomisc.service.aiohttp import AIOHTTPService
from sqlalchemy import create_engine

from .config import ApiGatewayConfig
from .database.models import Base
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
        self.engine = None
        super().__init__(address, port)

    async def create_application(self) -> web.Application:
        middlewares = list()
        if self.config.rest.cors.enabled:
            middlewares = [cors_middleware(allow_all=True)]

        app = web.Application(middlewares=middlewares)

        app["config"] = self.config

        self.engine = await self.create_engine()
        await self.create_database()

        app["db_engine"] = self.engine

        auth = self.config.rest.auth
        if auth is not None and auth.enabled:
            app.router.add_route("*", "/auth", authentication_default)
            for service in auth.services:
                app.router.add_route("*", f"/auth/{service.name}", authentication)

        app.router.add_route("POST", "/admin/login", AdminHandler.login)
        app.router.add_route("GET", "/admin/endpoints", AdminHandler.get_endpoints)
        app.router.add_route("GET", "/admin/rules", AdminHandler.get_rules)
        app.router.add_route("POST", "/admin/rules", AdminHandler.create_rule)
        app.router.add_route("PATCH", "/admin/rules/{id}", AdminHandler.update_rule)
        app.router.add_route("DELETE", "/admin/rules/{id}", AdminHandler.delete_rule)
        app.router.add_route("*", "/{endpoint:.*}", orchestrate)

        return app

    async def create_engine(self):
        DATABASE_URI = (
            f"postgresql+psycopg2://{self.config.database.user}:{self.config.database.password}@"
            f"{self.config.database.host}:{self.config.database.port}/{self.config.database.dbname}"
        )

        return create_engine(DATABASE_URI)

    async def create_database(self):
        Base.metadata.create_all(self.engine)
