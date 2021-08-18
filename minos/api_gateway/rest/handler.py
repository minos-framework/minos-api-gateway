import logging
from typing import (
    Any,
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

logger = logging.getLogger(__name__)


async def orchestrate(request: web.Request) -> web.Response:
    """ Orchestrate discovery and microservice call """
    discovery_host = request.app["config"].discovery.connection.host
    discovery_port = request.app["config"].discovery.connection.port
    discovery_path = request.app["config"].discovery.connection.path

    verb = request.method
    url = request.match_info["endpoint"]
    discovery_data = await discover(discovery_host, int(discovery_port), discovery_path, verb, url)

    microservice_response = await call(**discovery_data, original_req=request)
    return microservice_response


async def discover(host: str, port: int, path: str, verb: str, endpoint: str) -> dict[str, Any]:
    """Call discovery service and get microservice connection data.

    :param host: Optional discovery host name.
    :param port: Optional discovery port.
    :param path: Optional discovery path.
    :param verb: Optional verb.
    :param endpoint: Optional microservice url.
    :return: The response of the discovery.
    """

    url = URL.build(scheme="http", host=host, port=port, path=path, query={"verb": verb, "path": endpoint})
    try:
        async with ClientSession() as session:
            async with session.get(url=url) as response:
                if not response.ok:
                    raise web.HTTPBadGateway(text="The discovery response is not okay.")
                data = await response.json()
    except ClientConnectorError:
        raise web.HTTPGatewayTimeout(text="The discovery is not available.")

    data["port"] = int(data["port"])

    return data


# noinspection PyUnusedLocal
async def call(address: str, port: int, original_req: web.Request, **kwargs) -> web.Response:
    """Call microservice (redirect the original call)

    :param address: The ip of the microservices.
    :param port: The port of the microservice.
    :param kwargs: Additional named arguments.
    :param original_req
    :return: The web response to be retrieved to the client.
    """

    headers = original_req.headers
    url = original_req.url.with_scheme("http").with_host(address).with_port(port)
    method = original_req.method
    content = await original_req.text()

    logger.info(f"Redirecting {method!r} request to {url!r}...")

    try:
        async with ClientSession(headers=headers) as session:
            async with session.request(method=method, url=url, data=content) as response:
                return await _clone_response(response)
    except ClientConnectorError:
        raise web.HTTPServiceUnavailable(text="The requested endpoint is not available.")


# noinspection PyMethodMayBeStatic
async def _clone_response(response: ClientResponse) -> web.Response:
    return web.Response(
        body=await response.read(), status=response.status, reason=response.reason, headers=response.headers,
    )
