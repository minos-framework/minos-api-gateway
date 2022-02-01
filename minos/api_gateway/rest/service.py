import logging
from pathlib import (
    Path,
)

import aiohttp_jinja2
import jinja2
from aiohttp import (
    web,
)
from aiohttp_middlewares import (
    cors_middleware,
)
from aiomisc.service.aiohttp import (
    AIOHTTPService,
)
from sqlalchemy import (
    create_engine,
)

from .config import (
    ApiGatewayConfig,
)
from .database.models import (
    Base,
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

        # Administration routes
        aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader("minos/api_gateway/rest/backend/templates"))
        # app.router.add_static('/admin', path='minos/api_gateway/rest/backend', name='static',
        # follow_symlinks=True, show_index=True)
        app.router.add_route("*", "/administration", self.handler)
        app.router.add_route("GET", "/administration/{filename:.*}", self._serve_files)

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

    @aiohttp_jinja2.template("tmpl.jinja2")
    def handler(self, request):
        context = {}
        response = aiohttp_jinja2.render_template("index.html", request, context)
        response.headers["Content-Language"] = "es"
        return response

    async def _serve_files(self, request: web.Request) -> web.FileResponse:
        rel_url = request.match_info["filename"]

        path = Path(Path.cwd())
        self._directory = path.resolve()

        try:
            filename = Path(rel_url)
            if filename.anchor:
                # rel_url is an absolute name like
                # /static/\\machine_name\c$ or /static/D:\path
                # where the static dir is totally different
                raise web.HTTPForbidden()
            filepath = self._directory.joinpath("minos", "api_gateway", "rest", "backend", "admin", filename).resolve()

            # p = filepath.relative_to(self._directory)
            return web.FileResponse(path=filepath, status=200)

        except (ValueError, FileNotFoundError) as error:
            # relatively safe
            raise web.HTTPNotFound() from error
        except web.HTTPForbidden:
            raise
        except Exception as error:
            # perm error or other kind!
            request.app.logger.exception(error)
            raise web.HTTPNotFound() from error
