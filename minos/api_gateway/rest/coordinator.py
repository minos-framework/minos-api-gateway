import logging
from typing import (
    Any,
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
        discovery_data = await self.call_discovery_service(
            host=self.discovery_host, port=self.discovery_port, path=self.discovery_path
        )

        microservice_data = await self.call_microservice(discovery_data)

        return web.json_response(data=microservice_data)

    async def call_discovery_service(self, host: str, port: int, path: str):
        """ Call discovery service and get microservice connection data. """
        url = "http://{host}:{port}/{discovery_path}?name={name}".format(
            host=host, port=port, discovery_path=path, name=self.name
        )
        try:
            async with ClientHttp() as client:
                response = await client.get(url=url)
                data = await response.json()
        except Exception as e:
            raise aiohttp.web.HTTPBadRequest(text=str(e))

        data["port"] = int(data["port"])
        return data

    async def call_microservice(self, discovery_data: dict[str, Any]):
        """ Call microservice (redirect the original call) """

        headers = self.original_req.headers
        url = (
            self.original_req.url.with_scheme("http").with_host(discovery_data["ip"]).with_port(discovery_data["port"])
        )
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
