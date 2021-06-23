"""
Copyright (C) 2021 Clariteia SL

This file is part of minos framework.

Minos framework can not be copied and/or distributed without the express permission of Clariteia SL.
"""
import logging
from typing import (
    Optional,
)

import aiohttp
from aiohttp import (
    web,
)

from minos.api_gateway.common import (
    ClientHttp,
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

    async def orchestrate(self):
        """ Orchestrate discovery and microservice call """
        discovery_data = await self.call_discovery_service()
        microservice_data = await self.call_microservice(**discovery_data)
        return web.json_response(data=microservice_data)

    async def call_discovery_service(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        path: Optional[str] = None,
        name: Optional[str] = None,
    ):
        """ Call discovery service and get microservice connection data. """
        if host is None:
            host = self.discovery_host
        if port is None:
            port = self.discovery_port
        if path is None:
            path = self.discovery_path
        if name is None:
            name = self.name

        # noinspection HttpUrlsUsage
        url = f"http://{host}:{port}/{path}?name={name}"

        try:
            async with ClientHttp() as client:
                response = await client.get(url=url)
                data = await response.json()
        except Exception as e:
            raise aiohttp.web.HTTPBadRequest(text=str(e))

        data["port"] = int(data["port"])
        return data

    # noinspection PyUnusedLocal
    async def call_microservice(self, ip: str, port: int, **kwargs):
        """ Call microservice (redirect the original call) """

        headers = self.original_req.headers
        url = self.original_req.url.with_scheme("http").with_host(ip).with_port(port)
        method = self.original_req.method
        content = await self.original_req.text()

        logger.info(f"Redirecting {method!r} request to {url!r}...")

        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                request = session.request(method=method, url=url, data=content)
                async with request as response:
                    return await response.json()
        except Exception as e:
            raise aiohttp.web.HTTPBadRequest(text=str(e))
