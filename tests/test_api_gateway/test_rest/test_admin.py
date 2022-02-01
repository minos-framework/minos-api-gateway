import json
import os
import unittest
from unittest import mock

from aiohttp.test_utils import (
    AioHTTPTestCase,
    unittest_run_loop,
)

from minos.api_gateway.rest import (
    ApiGatewayConfig,
    ApiGatewayRestService,
)
from tests.mock_servers.server import MockServer
from tests.utils import BASE_PATH


class TestApiGatewayAdminLogin(AioHTTPTestCase):
    CONFIG_FILE_PATH = BASE_PATH / "config.yml"

    @mock.patch.dict(os.environ, {"API_GATEWAY_REST_CORS_ENABLED": "true"})
    def setUp(self) -> None:
        self.config = ApiGatewayConfig(self.CONFIG_FILE_PATH)
        super().setUp()

    def tearDown(self) -> None:
        super().tearDown()

    async def get_application(self):
        """
        Override the get_app method to return your application.
        """
        rest_service = ApiGatewayRestService(
            address=self.config.rest.host, port=self.config.rest.port, config=self.config
        )

        return await rest_service.create_application()

    @unittest_run_loop
    async def test_admin_login(self):
        url = "/admin/login"

        response = await self.client.request(
            "POST",
            url,
            data=json.dumps({"username": self.config.rest.admin.username, "password": self.config.rest.admin.password}),
        )

        self.assertEqual(200, response.status)
        self.assertIn("id", await response.text())
        self.assertIn("token", await response.text())

    @unittest_run_loop
    async def test_admin_login_no_data(self):
        url = "/admin/login"

        response = await self.client.request("POST", url)

        self.assertEqual(401, response.status)
        self.assertDictEqual({"error": "Something went wrong!."}, json.loads(await response.text()))

    @unittest_run_loop
    async def test_admin_login_wrong_data(self):
        url = "/admin/login"

        response = await self.client.request("POST", url, data=json.dumps({"username": "abc", "password": "test"}))

        self.assertEqual(401, response.status)
        self.assertDictEqual({"error": "Wrong username or password!."}, json.loads(await response.text()))


class TestApiGatewayAdminEndpoints(AioHTTPTestCase):
    CONFIG_FILE_PATH = BASE_PATH / "config.yml"

    @mock.patch.dict(os.environ, {"API_GATEWAY_REST_CORS_ENABLED": "true"})
    def setUp(self) -> None:
        self.config = ApiGatewayConfig(self.CONFIG_FILE_PATH)

        self.discovery = MockServer(host=self.config.discovery.host, port=self.config.discovery.port,)
        self.discovery.add_json_response(
            "/endpoints", [{"one": 1}, {"two": 2}],
        )

        self.discovery.start()
        super().setUp()

    def tearDown(self) -> None:
        self.discovery.shutdown_server()
        super().tearDown()

    async def get_application(self):
        """
        Override the get_app method to return your application.
        """
        rest_service = ApiGatewayRestService(
            address=self.config.rest.host, port=self.config.rest.port, config=self.config
        )

        return await rest_service.create_application()

    @unittest_run_loop
    async def test_admin_get_endpoints(self):
        url = "/admin/endpoints"

        response = await self.client.request("GET", url)

        self.assertEqual(200, response.status)
        self.assertIn("one", await response.text())
        self.assertIn("two", await response.text())


class TestApiGatewayAdminEndpointsUnavailable(AioHTTPTestCase):
    CONFIG_FILE_PATH = BASE_PATH / "config.yml"

    @mock.patch.dict(os.environ, {"API_GATEWAY_REST_CORS_ENABLED": "true"})
    def setUp(self) -> None:
        self.config = ApiGatewayConfig(self.CONFIG_FILE_PATH)
        super().setUp()

    def tearDown(self) -> None:
        super().tearDown()

    async def get_application(self):
        """
        Override the get_app method to return your application.
        """
        rest_service = ApiGatewayRestService(
            address=self.config.rest.host, port=self.config.rest.port, config=self.config
        )

        return await rest_service.create_application()

    @unittest_run_loop
    async def test_admin_get_endpoints(self):
        url = "/admin/endpoints"

        response = await self.client.request("GET", url)

        self.assertEqual(503, response.status)
        self.assertDictEqual({"error": "The requested endpoint is not available."}, json.loads(await response.text()))


class TestApiGatewayAdminRules(AioHTTPTestCase):
    CONFIG_FILE_PATH = BASE_PATH / "config.yml"

    @mock.patch.dict(os.environ, {"API_GATEWAY_REST_CORS_ENABLED": "true"})
    def setUp(self) -> None:
        self.config = ApiGatewayConfig(self.CONFIG_FILE_PATH)
        super().setUp()

    def tearDown(self) -> None:
        super().tearDown()

    async def get_application(self):
        """
        Override the get_app method to return your application.
        """
        rest_service = ApiGatewayRestService(
            address=self.config.rest.host, port=self.config.rest.port, config=self.config
        )

        return await rest_service.create_application()

    @unittest_run_loop
    async def test_admin_get_rules(self):
        url = "/admin/rules"

        response = await self.client.request("GET", url)

        self.assertEqual(200, response.status)

    @unittest_run_loop
    async def test_admin_create_rule(self):
        url = "/admin/rules"

        response = await self.client.request(
            "POST",
            url,
            data=json.dumps({"service": "merchants", "rule": "*://*/merchants/*", "methods": ["GET", "POST"]}),
        )

        self.assertEqual(200, response.status)

    @unittest_run_loop
    async def test_admin_update_rule(self):
        url = "/admin/rules"

        res = await self.client.request(
            "POST",
            url,
            data=json.dumps({"service": "merchants", "rule": "test_rule_update", "methods": ["GET", "POST"]}),
        )

        data = json.loads(await res.text())

        self.assertEqual(200, res.status)

        url = f"/admin/rules/{data['id']}"

        response = await self.client.request(
            "PATCH",
            url,
            data=json.dumps({"service": "merchants_modified", "rule": "*://*/merchants/*", "methods": ["GET", "POST"]}),
        )

        self.assertEqual(200, response.status)

    @unittest_run_loop
    async def test_admin_delete_rule(self):
        url = "/admin/rules"

        res = await self.client.request(
            "POST",
            url,
            data=json.dumps({"service": "merchants", "rule": "test_rule_delete", "methods": ["GET", "POST"]}),
        )

        data = json.loads(await res.text())

        self.assertEqual(200, res.status)

        url = f"/admin/rules/{data['id']}"

        response = await self.client.request("DELETE", url)

        self.assertEqual(200, response.status)


if __name__ == "__main__":
    unittest.main()
