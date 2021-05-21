# Copyright (C) 2020 Clariteia SL
#
# This file is part of minos framework.
#
# Minos framework can not be copied and/or distributed without the express
# permission of Clariteia SL.

import typing as t

from aiohttp import (
    web,
)

from minos.api_gateway.common import (
    MinosConfig,
    RESTService,
)


class ApiGatewayRestService(RESTService):
    def __init__(self, config: MinosConfig, app: web.Application = web.Application(), **kwds: t.Any):
        super().__init__(
            address=config.rest.connection.host,
            port=config.rest.connection.port,
            endpoints=config.rest.endpoints,
            config=config,
            app=app,
            **kwds
        )
