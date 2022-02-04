import json
import logging
import secrets
from datetime import (
    datetime,
)
from typing import (
    Any,
    Optional,
)

from aiohttp import (
    ClientConnectorError,
    ClientResponse,
    ClientSession,
    web,
)
from yarl import (
    URL,
)

from minos.api_gateway.rest.database.models import (
    AuthRule,
)
from minos.api_gateway.rest.urlmatch.authmatch import (
    AuthMatch,
)

from .database.repository import (
    Repository,
)

logger = logging.getLogger(__name__)


async def orchestrate(request: web.Request) -> web.Response:
    """ Orchestrate discovery and microservice call """
    discovery_host = request.app["config"].discovery.host
    discovery_port = request.app["config"].discovery.port

    verb = request.method
    url = f"/{request.match_info['endpoint']}"

    discovery_data = await discover(discovery_host, int(discovery_port), "/microservices", verb, url)

    auth = request.app["config"].rest.auth
    user = None
    if auth is not None and auth.enabled:
        if await check_auth(request=request, service=request.url.parts[1], url=str(request.url), method=request.method):
            response = await validate_token(request)
            user = json.loads(response)
            user = user["uuid"]

    microservice_response = await call(**discovery_data, original_req=request, user=user)
    return microservice_response


async def check_auth(request: web.Request, service: str, url: str, method: str) -> bool:
    records = Repository(request.app["db_engine"]).get_by_service(service)
    return AuthMatch.match(url=url, method=method, records=records)


async def authentication_default(request: web.Request) -> web.Response:
    """ Orchestrate discovery and microservice call """
    auth_host = request.app["config"].rest.auth.host
    auth_port = request.app["config"].rest.auth.port
    auth_path = request.app["config"].rest.auth.path
    default_service = request.app["config"].rest.auth.default

    url = URL(f"http://{auth_host}:{auth_port}{auth_path}/{default_service}")

    return await authentication_call(request, url)


async def login_default(request: web.Request) -> web.Response:
    """ Orchestrate discovery and microservice call """
    auth_host = request.app["config"].rest.auth.host
    auth_port = request.app["config"].rest.auth.port
    auth_path = request.app["config"].rest.auth.path
    default_service = request.app["config"].rest.auth.default

    url = URL(f"http://{auth_host}:{auth_port}{auth_path}/{default_service}/login")

    return await authentication_call(request, url)


async def authentication(request: web.Request) -> web.Response:
    """ Orchestrate discovery and microservice call """

    auth_host = request.app["config"].rest.auth.host
    auth_port = request.app["config"].rest.auth.port

    url = URL(f"http://{auth_host}:{auth_port}{request.path}")

    return await authentication_call(request, url)


async def authentication_call(request: web.Request, url: URL) -> web.Response:
    """ Orchestrate discovery and microservice call """
    headers = request.headers.copy()
    data = await request.read()

    try:
        async with ClientSession() as session:
            async with session.request(headers=headers, method=request.method, url=url, data=data) as response:
                return await _clone_response(response)
    except ClientConnectorError:
        raise web.HTTPServiceUnavailable(text="The requested endpoint is not available.")


async def validate_token(request: web.Request):
    """ Orchestrate discovery and microservice call """
    auth_host = request.app["config"].rest.auth.host
    auth_port = request.app["config"].rest.auth.port
    auth_path = request.app["config"].rest.auth.path

    auth_url = URL(f"http://{auth_host}:{auth_port}{auth_path}/validate-token")

    headers = request.headers.copy()
    data = await request.read()

    try:
        async with ClientSession() as session:
            async with session.request(method="POST", url=auth_url, data=data, headers=headers) as response:
                resp = await _clone_response(response)

                if not response.ok:
                    raise web.HTTPUnauthorized(text="The given request does not have authorization to be forwarded.")
                return resp.text

    except ClientConnectorError:
        raise web.HTTPServiceUnavailable(text="The requested endpoint is not available.")


async def discover(host: str, port: int, path: str, verb: str, endpoint: str) -> dict[str, Any]:
    """Call discovery service and get microservice connection data.

    :param host: Discovery host name.
    :param port: Discovery port.
    :param path: Discovery path.
    :param verb: Endpoint Verb.
    :param endpoint: Endpoint url.
    :return: The response of the discovery.
    """

    url = URL.build(scheme="http", host=host, port=port, path=path, query={"verb": verb, "path": endpoint})
    try:
        async with ClientSession() as session:
            async with session.get(url=url) as response:
                if not response.ok:
                    if response.status == 404:
                        raise web.HTTPNotFound(text=f"The {endpoint!r} path is not available for {verb!r} method.")
                    raise web.HTTPBadGateway(text="The Discovery Service response is wrong.")

                data = await response.json()
    except ClientConnectorError:
        raise web.HTTPGatewayTimeout(text="The Discovery Service is not available.")

    data["port"] = int(data["port"])

    return data


# noinspection PyUnusedLocal
async def call(address: str, port: int, original_req: web.Request, user: Optional[str], **kwargs) -> web.Response:
    """Call microservice (redirect the original call)

    :param address: The ip of the microservices.
    :param port: The port of the microservice.
    :param original_req: The original request.
    :param kwargs: Additional named arguments.
    :param user: User that makes the request
    :return: The web response to be retrieved to the client.
    """

    headers = original_req.headers.copy()
    if user is not None:
        headers["X-User"] = user
    else:  # Enforce that the 'User' entry is only generated by the auth system.
        # noinspection PyTypeChecker
        headers.pop("X-User", None)

    url = original_req.url.with_scheme("http").with_host(address).with_port(port)
    method = original_req.method
    data = await original_req.read()

    logger.info(f"Redirecting {method!r} request to {url!r}...")

    try:
        async with ClientSession() as session:
            async with session.request(headers=headers, method=method, url=url, data=data) as response:
                return await _clone_response(response)
    except ClientConnectorError:
        raise web.HTTPServiceUnavailable(text="The requested endpoint is not available.")


# noinspection PyMethodMayBeStatic
async def _clone_response(response: ClientResponse) -> web.Response:
    return web.Response(
        body=await response.read(), status=response.status, reason=response.reason, headers=response.headers,
    )


class AdminHandler:
    @staticmethod
    async def login(request: web.Request) -> web.Response:
        """ Orchestrate discovery and microservice call """
        username = request.app["config"].rest.admin.username
        password = request.app["config"].rest.admin.password

        try:
            content = await request.json()

            if "user" not in content and "password" not in content:
                return web.json_response(
                    {"error": "Wrong data. Provide user and password."}, status=web.HTTPUnauthorized.status_code
                )

            if username == content["username"] and password == content["password"]:
                return web.json_response({"id": 1, "token": secrets.token_hex(20)})

            return web.json_response({"error": "Wrong username or password!."}, status=web.HTTPUnauthorized.status_code)
        except Exception:
            return web.json_response({"error": "Something went wrong!."}, status=web.HTTPUnauthorized.status_code)

    @staticmethod
    async def get_endpoints(request: web.Request) -> web.Response:
        discovery_host = request.app["config"].discovery.host
        discovery_port = request.app["config"].discovery.port

        url = URL.build(scheme="http", host=discovery_host, port=discovery_port, path="/endpoints")

        try:
            async with ClientSession() as session:
                async with session.get(url=url) as response:
                    return await _clone_response(response)
        except ClientConnectorError:
            return web.json_response(
                {"error": "The requested endpoint is not available."}, status=web.HTTPServiceUnavailable.status_code
            )

    @staticmethod
    async def get_rules(request: web.Request) -> web.Response:
        records = Repository(request.app["db_engine"]).get_all()
        return web.json_response(records)

    @staticmethod
    async def create_rule(request: web.Request) -> web.Response:
        try:
            content = await request.json()

            if "service" not in content and "rule" not in content and "methods" not in content:
                return web.json_response(
                    {"error": "Wrong data. Provide 'service', 'rule' and 'methods' parameters."},
                    status=web.HTTPBadRequest.status_code,
                )

            now = datetime.now()

            rule = AuthRule(
                service=content["service"],
                rule=content["rule"],
                methods=content["methods"],
                created_at=now,
                updated_at=now,
            )

            record = Repository(request.app["db_engine"]).create(rule)

            return web.json_response(record)
        except Exception as e:
            return web.json_response({"error": str(e)}, status=web.HTTPBadRequest.status_code)

    @staticmethod
    async def update_rule(request: web.Request) -> web.Response:
        try:
            id = int(request.url.name)
            content = await request.json()
            Repository(request.app["db_engine"]).update(id=id, **content)
            return web.json_response(status=web.HTTPOk.status_code)
        except Exception as e:
            return web.json_response({"error": str(e)}, status=web.HTTPBadRequest.status_code)

    @staticmethod
    async def delete_rule(request: web.Request) -> web.Response:
        try:
            id = int(request.url.name)
            Repository(request.app["db_engine"]).delete(id)
            return web.json_response(status=web.HTTPOk.status_code)
        except Exception as e:
            return web.json_response({"error": str(e)}, status=web.HTTPBadRequest.status_code)
