"""Exception hierarchy for the payments package.

Views should catch ``PaymentError`` (the common base class) and show the
exception message to the user; all lower-level gateway/network details are
logged separately and never leaked directly to the client.
"""


class PaymentError(Exception):
    """Base class for all payment related errors."""


class PaymentConfigurationError(PaymentError):
    """Raised when the payment gateway is misconfigured (missing/invalid settings)."""


class PaymentGatewayError(PaymentError):
    """Raised when the gateway request itself fails (network error, bad response,
    non-success result code returned while creating a transaction, ...)."""


class PaymentVerificationError(PaymentError):
    """Raised when verifying a transaction with the gateway fails unexpectedly."""


class InvalidCallbackError(PaymentError):
    """Raised when a callback request from the gateway is missing required data
    or does not match any known order."""
