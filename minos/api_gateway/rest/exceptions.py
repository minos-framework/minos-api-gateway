class ApiGatewayException(Exception):
    """Base Api Gateway Exception."""


class InvalidAuthenticationException(ApiGatewayException):
    """Exception to be raised when authentication is not valid."""


class NoTokenException(ApiGatewayException):
    """Exception to be raised when token is not available."""


class ApiGatewayConfigException(ApiGatewayException):
    """Base config exception."""
