"""
Copyright (C) 2021 Clariteia SL

This file is part of minos framework.

Minos framework can not be copied and/or distributed without the express permission of Clariteia SL.
"""
import logging
from typing import (
    Any,
    Optional,
)

import aiohttp
from aiohttp import (
    ClientConnectorError,
    ClientResponse,
    ClientSession,
    web,
)
from aiohttp.web_response import (
    Response,
)
from yarl import (
    URL,
)

from minos.api_gateway.common import (
    MinosConfig,
)

logger = logging.getLogger(__name__)


class MicroserviceCallCoordinator:
    """Microservice Call Coordinator class."""

    def __init__(
        self,
        config: MinosConfig,
        request: web.Request,
        discovery_host: str = None,
        discovery_port: str = None,
        discovery_path: str = None,
    ):
        self.name = request.url.parent.name if len(request.url.parent.name) > 0 else request.url.name
        self.config = config
        self.original_req = request
        self.discovery_host = config.discovery.connection.host if discovery_host is None else discovery_host
        self.discovery_port = config.discovery.connection.port if discovery_port is None else discovery_port
        self.discovery_path = config.discovery.connection.path if discovery_path is None else discovery_path

    async def orchestrate(self) -> Response:
        """ Orchestrate discovery and microservice call """
        discovery_data = await self.call_discovery_service()
        microservice_response = await self.call_microservice(**discovery_data)
        return microservice_response

    async def call_discovery_service(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        path: Optional[str] = None,
        name: Optional[str] = None,
    ) -> dict[str, Any]:
        """ Call discovery service and get microservice connection data. """
        if host is None:
            host = self.discovery_host
        if port is None:
            port = self.discovery_port
        if path is None:
            path = self.discovery_path
        if name is None:
            name = self.name

        url = URL.build(scheme="http", host=host, port=port, path=path, query={"name": name})
        try:
            async with ClientSession() as session:
                async with session.get(url=url) as response:
                    if not response.ok:
                        raise aiohttp.web.HTTPBadGateway(text="The discovery response is not okay.")
                    data = await response.json()
        except ClientConnectorError:
            raise aiohttp.web.HTTPGatewayTimeout(text="The discovery is not available.")

        if "status" not in data or not data["status"]:
            raise aiohttp.web.HTTPServiceUnavailable(text="The requested endpoint is not available.")

        data["port"] = int(data["port"])

        return data

    # noinspection PyUnusedLocal
    async def call_microservice(self, ip: str, port: int, **kwargs) -> Response:
        """ Call microservice (redirect the original call) """

        headers = self.original_req.headers
        url = self.original_req.url.with_scheme("http").with_host(ip).with_port(port)
        method = self.original_req.method
        content = await self.original_req.text()

        logger.info(f"Redirecting {method!r} request to {url!r}...")

        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.request(method=method, url=url, data=content) as response:
                    return await self._clone_response(response)
        except ClientConnectorError:
            raise aiohttp.web.HTTPServiceUnavailable(text="The requested endpoint is not available.")

    # noinspection PyMethodMayBeStatic
    async def _clone_response(self, response: ClientResponse) -> Response:
        return Response(
            body=await response.read(), status=response.status, reason=response.reason, headers=response.headers,
        )
