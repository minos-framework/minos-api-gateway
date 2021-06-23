"""
Copyright (C) 2021 Clariteia SL

This file is part of minos framework.

Minos framework can not be copied and/or distributed without the express permission of Clariteia SL.
"""
from aiohttp import (
    web,
)

from minos.api_gateway.common import (
    MinosConfig,
)

from .coordinator import (
    MicroserviceCallCoordinator,
)


class DefaultController:
    """Default Controller class."""

    def __init__(self, coordinator_cls: type = MicroserviceCallCoordinator):
        self.coordinator_cls = coordinator_cls

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    async def default(self, request: web.Request, config: MinosConfig, **kwargs) -> web.Response:
        """Default action method.

        :param request: The request to be redirected.
        :param config: The minos config.
        :param kwargs: Additional named arguments.
        :return: A ``web.Response`` instance.
        """
        coordinator = self.coordinator_cls(config, request)
        response = await coordinator.orchestrate()
        return response
