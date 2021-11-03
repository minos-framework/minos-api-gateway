class ApiGatewayException(Exception):
    """Base Api Gateway Exception."""


class NoTokenException(ApiGatewayException):
    """Exception to be raised when token is not available."""


class ApiGatewayConfigException(ApiGatewayException):
    """Base config exception."""
