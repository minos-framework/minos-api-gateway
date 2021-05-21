import json

from aiohttp import web
import aiohttp
from minos.api_gateway.common import (
    ClientHttp,
    MinosConfig,
)


class MicroserviceCallCoordinator:
    def __init__(
        self, config: MinosConfig, request: web.Request, discovery_host: str = None, discovery_port: str = None
    ):
        self.name = request.url.name
        self.config = config
        self.original_req = request
        self.discovery_host = config.discovery.connection.host if discovery_host is None else discovery_host
        self.discovery_port = config.discovery.connection.port if discovery_port is None else discovery_port

    async def orchestrate(self):
        """ Orchestrate discovery and microservice call """
        status, text = await self.call_discovery_service(
            host=self.discovery_host, port=self.discovery_port, path="discover", name=self.name
        )

        if status:
            data = json.loads(text)
            status, response = await self.call_microservice(data)

            if status:
                return web.Response(text=response, status=200)
            else:
                return web.Response(text="Error connecting to microservice.", status=400)
        else:
            return web.Response(text="Non existing/registered microservice.", status=400)

    async def call_discovery_service(self, host: str, port: int, path: str, name: str):
        """ Call discovery service and get microservice connection data. """
        url = "http://{host}:{port}/{discovery_path}?name={name}".format(
            host=host, port=port, discovery_path=path, name=name
        )
        try:
            async with ClientHttp() as client:
                response = await client.get(url=url)
                data = await response.text()
            return True, data
        except Exception:
            return False, None

    async def call_microservice(self, data: dict):
        """ Call microservice (redirect the original call) """

        req_data = await self.original_req.text()

        url = "http://{host}:{port}{path}".format(host=data["ip"], port=data["port"], path=self.original_req.url.path)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(method=self.original_req.method, url=url, data=req_data) as resp:
                    data = await resp.text()

            return True, data
        except Exception:
            return False, None
