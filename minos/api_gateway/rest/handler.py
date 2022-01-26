import json
import logging
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
from yarl import URL

from minos.api_gateway.rest.urlmatch.authmatch import AuthMatch

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
        if AuthMatch.match(
            url=str(request.url), method=request.method, endpoints=request.app["config"].rest.auth.endpoints
        ):
            response = await validate_token(request)
            user = json.loads(response)
            user = user["uuid"]

    microservice_response = await call(**discovery_data, original_req=request, user=user)
    return microservice_response


async def authentication_default(request: web.Request) -> web.Response:
    """ Orchestrate discovery and microservice call """
    auth_host = request.app["config"].rest.auth.host
    auth_port = request.app["config"].rest.auth.port
    auth_path = request.app["config"].rest.auth.path
    default_service = request.app["config"].rest.auth.default

    url = URL(f"http://{auth_host}:{auth_port}{auth_path}/{default_service}")

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
