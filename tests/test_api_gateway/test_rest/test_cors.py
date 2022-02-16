import os
from unittest import (
    mock,
)

import attr
from aiohttp.test_utils import (
    AioHTTPTestCase,
)
from aiohttp_middlewares.cors import (
    ACCESS_CONTROL_ALLOW_HEADERS,
    ACCESS_CONTROL_ALLOW_METHODS,
    ACCESS_CONTROL_ALLOW_ORIGIN,
    DEFAULT_ALLOW_HEADERS,
    DEFAULT_ALLOW_METHODS,
)

from minos.api_gateway.rest import (
    ApiGatewayConfig,
    ApiGatewayRestService,
)
from tests.mock_servers.server import (
    MockServer,
)
from tests.utils import (
    BASE_PATH,
)


class TestApiGatewayCORS(AioHTTPTestCase):
    CONFIG_FILE_PATH = BASE_PATH / "config-auth-disabled.yml"
    TEST_DENIED_ORIGIN = "https://www.google.com"
    TEST_ORIGIN = "http://localhost:3000"

    @mock.patch.dict(os.environ, {"API_GATEWAY_REST_CORS_ENABLED": "true"})
    def setUp(self) -> None:
        self.config = ApiGatewayConfig(self.CONFIG_FILE_PATH)

        self.discovery = MockServer(host=self.config.discovery.host, port=self.config.discovery.port,)
        self.discovery.add_json_response(
            "/microservices", {"address": "localhost", "port": "5568", "status": True},
        )

        self.microservice = MockServer(host="localhost", port=5568)
        self.microservice.add_json_response(
            "/order/5", "Microservice call correct!!!", methods=("GET", "PUT", "PATCH", "DELETE",)
        )
        self.microservice.add_json_response("/order", "Microservice call correct!!!", methods=("POST",))

        self.discovery.start()
        self.microservice.start()
        super().setUp()

    def tearDown(self) -> None:
        self.discovery.shutdown_server()
        self.microservice.shutdown_server()
        super().tearDown()

    async def get_application(self):
        """
        Override the get_app method to return your application.
        """
        rest_service = ApiGatewayRestService(
            address=self.config.rest.host, port=self.config.rest.port, config=self.config
        )

        return await rest_service.create_application()

    @staticmethod
    def check_allow_origin(
        response, origin, *, allow_headers=DEFAULT_ALLOW_HEADERS, allow_methods=DEFAULT_ALLOW_METHODS,
    ):
        assert response.headers[ACCESS_CONTROL_ALLOW_ORIGIN] == origin
        if allow_headers:
            assert response.headers[ACCESS_CONTROL_ALLOW_HEADERS] == ", ".join(allow_headers)
        if allow_methods:
            assert response.headers[ACCESS_CONTROL_ALLOW_METHODS] == ", ".join(allow_methods)

    async def test_cors_enabled(self):
        method = "GET"
        extra_headers = {}
        expected_origin = "*"
        expected_allow_headers = None
        expected_allow_methods = None
        url = "/order/5?verb=GET&path=12324"

        kwargs = {}
        if expected_allow_headers is not attr.NOTHING:
            kwargs["allow_headers"] = expected_allow_headers
        if expected_allow_methods is not attr.NOTHING:
            kwargs["allow_methods"] = expected_allow_methods

        self.check_allow_origin(
            await self.client.request(method, url, headers={"Origin": self.TEST_ORIGIN, **extra_headers}),
            expected_origin,
            **kwargs,
        )
