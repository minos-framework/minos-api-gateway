class ApiGatewayException(Exception):
    """TODO"""


class InvalidAuthenticationException(ApiGatewayException):
    """TODO"""


class NoTokenException(ApiGatewayException):
    """TODO"""


class ApiGatewayConfigException(ApiGatewayException):
    """Base config exception."""
