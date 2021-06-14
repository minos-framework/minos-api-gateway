"""
Copyright (C) 2021 Clariteia SL

This file is part of minos framework.

Minos framework can not be copied and/or distributed without the express permission of Clariteia SL.
"""

import logging
from typing import (
    NoReturn,
)

from aiomisc import (
    entrypoint,
)
from aiomisc.entrypoint import (
    Entrypoint,
)
from cached_property import (
    cached_property,
)

from minos.api_gateway.common import (
    MinosConfig,
)

logger = logging.getLogger(__name__)


class EntrypointLauncher:
    """EntryPoint Launcher class."""

    def __init__(self, config: MinosConfig, services: tuple, *args, **kwargs):
        self.config = config
        self.services = services

    def launch(self) -> NoReturn:
        """Launch a new execution and keeps running forever..

        :return: This method does not return anything.
        """
        logger.info("Starting API Gateway...")
        with self.entrypoint as loop:
            logger.info("API Gateway is up and running!")
            loop.run_forever()

    @cached_property
    def entrypoint(self) -> Entrypoint:
        """Entrypoint instance.

        :return: An ``Entrypoint`` instance.
        """

        return entrypoint(*self.services)  # pragma: no cover
