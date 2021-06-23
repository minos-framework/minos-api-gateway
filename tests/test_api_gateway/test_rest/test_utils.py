"""
Copyright (C) 2021 Clariteia SL

This file is part of minos framework.

Minos framework can not be copied and/or distributed without the express permission of Clariteia SL.
"""

import unittest
from unittest.mock import (
    MagicMock,
)

from minos.api_gateway.rest import (
    DefaultController,
)


class _Foo:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    async def orchestrate(self):
        pass


async def _fn(*args, **kwargs):
    pass


class TestDefaultController(unittest.IsolatedAsyncioTestCase):
    async def test_default(self):
        mock = MagicMock(side_effect=_fn)
        _Foo.orchestrate = mock
        controller = DefaultController(_Foo)
        await controller.default("one", "two")
        self.assertEqual(1, mock.call_count)


if __name__ == "__main__":
    unittest.main()
