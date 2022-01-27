import json
import os
import unittest
from unittest import (
    mock,
)

from aiohttp.test_utils import (
    AioHTTPTestCase,
    unittest_run_loop,
)

from minos.api_gateway.rest import (
    ApiGatewayConfig,
    ApiGatewayRestService,
)
from tests.utils import (
    BASE_PATH,
)


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


if __name__ == "__main__":
    unittest.main()
