import json

import aiohttp
from aiohttp import (
    web,
)

from minos.api_gateway.common import (
    ClientHttp,
    MinosConfig,
)


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
        text = await self.call_discovery_service(
            host=self.discovery_host, port=self.discovery_port, path=self.discovery_path
        )

        data = json.loads(text)
        response = await self.call_microservice(data)

        return web.json_response(data=response)

    async def call_discovery_service(self, host: str, port: int, path: str):
        """ Call discovery service and get microservice connection data. """
        url = "http://{host}:{port}/{discovery_path}?name={name}".format(
            host=host, port=port, discovery_path=path, name=self.name
        )
        try:
            async with ClientHttp() as client:
                response = await client.get(url=url)
                data = await response.text()
            return data
        except Exception as e:
            raise aiohttp.web.HTTPBadRequest(text=str(e))

    async def call_microservice(self, data: dict):
        """ Call microservice (redirect the original call) """

        req_data = await self.original_req.text()

        url = "http://{host}:{port}{path}".format(host=data["ip"], port=data["port"], path=self.original_req.url.path)

        try:
            async with aiohttp.ClientSession(headers=self.original_req.headers) as session:
                async with session.request(method=self.original_req.method, url=url, data=req_data) as resp:
                    data = await resp.text()
                    return data

        except Exception as e:
            raise aiohttp.web.HTTPBadRequest(text=str(e))
