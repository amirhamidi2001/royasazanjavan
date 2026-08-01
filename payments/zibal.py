"""Thin wrapper around the official Zibal REST API.

Only the two endpoints required for a standard "IPG" payment flow are
implemented: request (create transaction) and verify.

Reference: https://docs.zibal.ir/
No unofficial/community client libraries are used - this talks to the
official REST endpoints directly over HTTPS using ``requests``.

All network/parsing failures are converted into ``PaymentGatewayError`` so
that callers only ever have to deal with a single exception type. Business
rules (which result codes mean "success", how to build the redirect URL for
the merchant's configuration, etc.) are intentionally kept out of this
module - see ``payments/services.py`` for that.
"""

import logging

import requests
from django.conf import settings

from .exceptions import PaymentGatewayError

logger = logging.getLogger("payments.zibal")


class ZibalClient:
    """Low-level HTTP client for the Zibal payment gateway REST API."""

    def __init__(self):
        self.merchant = settings.ZIBAL_MERCHANT
        self.request_url = settings.ZIBAL_REQUEST_URL
        self.verify_url = settings.ZIBAL_VERIFY_URL
        self.startpay_url = settings.ZIBAL_STARTPAY_URL
        self.timeout = settings.ZIBAL_REQUEST_TIMEOUT

    def _post(self, url, payload):
        """POST a JSON payload to Zibal and return the parsed JSON response.

        Raises ``PaymentGatewayError`` on any network, timeout, HTTP or
        JSON-decoding failure so callers never have to deal with raw
        ``requests`` exceptions.
        """
        try:
            response = requests.post(url, json=payload, timeout=self.timeout)
        except requests.exceptions.Timeout as exc:
            logger.error("Zibal request timed out: url=%s", url)
            raise PaymentGatewayError(
                "اتصال به درگاه پرداخت زیبال با تأخیر مواجه شد. لطفاً دوباره تلاش کنید"
            ) from exc
        except requests.exceptions.RequestException as exc:
            logger.error("Zibal request failed: url=%s error=%s", url, exc)
            raise PaymentGatewayError("خطا در اتصال به درگاه پرداخت زیبال") from exc

        try:
            data = response.json()
        except ValueError as exc:
            logger.error(
                "Zibal returned a non-JSON response: url=%s status=%s body=%s",
                url,
                response.status_code,
                response.text[:500],
            )
            raise PaymentGatewayError(
                "پاسخ نامعتبر از درگاه پرداخت زیبال دریافت شد"
            ) from exc

        logger.debug("Zibal response: url=%s data=%s", url, data)
        return data

    def request_payment(
        self,
        amount,
        callback_url,
        description,
        order_id,
        mobile=None,
    ):
        """Create a new transaction ("request" step) and return the raw
        JSON response from Zibal (contains ``trackId`` and ``result``)."""
        payload = {
            "merchant": self.merchant,
            "amount": amount,
            "callbackUrl": callback_url,
            "description": description,
            "orderId": str(order_id),
        }
        if mobile:
            payload["mobile"] = mobile

        logger.info("Zibal request_payment: order_id=%s amount=%s", order_id, amount)
        return self._post(self.request_url, payload)

    def verify_payment(self, track_id):
        """Verify a transaction and return the raw JSON response from Zibal
        (contains ``result``, ``refNumber``, ``status``, ``amount``, ...)."""
        payload = {
            "merchant": self.merchant,
            "trackId": track_id,
        }
        logger.info("Zibal verify_payment: track_id=%s", track_id)
        return self._post(self.verify_url, payload)

    def get_start_pay_url(self, track_id):
        """Build the URL the user's browser must be redirected to in order
        to complete the payment on Zibal's gateway page."""
        return f"{self.startpay_url}/{track_id}"
