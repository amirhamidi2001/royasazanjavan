"""Zibal payment orchestration.

``PaymentService`` is the single entry point views should use. It:

- wraps every state-changing operation in ``transaction.atomic()`` with a
  row lock (``select_for_update``) so concurrent/duplicate callbacks cannot
  double-verify or double-credit an order,
- normalizes Zibal's responses into small dataclasses so the calling code
  (views) never has to know about gateway-specific field names.

Business logic that belongs to orders (creating the order, enrolling the
user in courses, etc.) is untouched and still lives in ``orders.models``.

Zibal is the only supported payment gateway for this project, in both
development and production.
"""

import logging
from dataclasses import dataclass
from typing import Optional

from django.db import transaction

from .exceptions import PaymentError, PaymentGatewayError, PaymentVerificationError
from .zibal import ZibalClient

logger = logging.getLogger("payments.services")


# ---------------------------------------------------------------------------
# Result value objects
# ---------------------------------------------------------------------------


@dataclass
class PaymentRequestResult:
    """Result of successfully creating a transaction with Zibal."""

    track_id: str
    redirect_url: str
    raw_response: dict


@dataclass
class PaymentVerifyResult:
    """Result of verifying a transaction with Zibal."""

    success: bool
    reference_id: Optional[str]
    raw_response: dict
    message: str = ""


# ---------------------------------------------------------------------------
# Gateway
# ---------------------------------------------------------------------------


class ZibalGateway:
    """Zibal payment gateway integration."""

    name = "zibal"

    #: https://docs.zibal.ir/ - "result" codes returned by both the
    #: request and verify endpoints.
    RESULT_SUCCESS = 100
    RESULT_ALREADY_VERIFIED = 201

    RESULT_MESSAGES = {
        100: "تراکنش با موفقیت انجام شد",
        102: "merchant یافت نشد",
        103: "merchant غیرفعال است",
        104: "merchant نامعتبر است",
        105: "مبلغ بایستی بزرگتر از ۱٬۰۰۰ ریال باشد",
        106: "callbackUrl نامعتبر می‌باشد (شروع با http یا https)",
        113: "مبلغ تراکنش از سقف مجاز بیشتر است",
        201: "این تراکنش قبلاً تایید شده است",
        202: "سفارش پرداخت نشده یا ناموفق بوده است",
        203: "trackId نامعتبر می‌باشد",
    }

    def __init__(self):
        self.client = ZibalClient()

    def request_payment(self, order, callback_url):
        # Zibal amounts are expressed in Rials, while Order.final_price is
        # stored in Tomans. 1 Toman = 10 Rials.
        amount_rial = int(order.final_price) * 10
        description = f"پرداخت سفارش {order.order_number}"

        response = self.client.request_payment(
            amount=amount_rial,
            callback_url=callback_url,
            description=description,
            order_id=order.order_number,
            mobile=order.phone,
        )

        result_code = response.get("result")
        if result_code != self.RESULT_SUCCESS:
            message = self.RESULT_MESSAGES.get(
                result_code, response.get("message") or "خطا در ایجاد تراکنش پرداخت"
            )
            logger.warning(
                "Zibal request_payment failed: order=%s result=%s",
                order.order_number,
                result_code,
            )
            raise PaymentGatewayError(message)

        track_id = response.get("trackId")
        if not track_id:
            logger.error(
                "Zibal request_payment succeeded but returned no trackId: order=%s",
                order.order_number,
            )
            raise PaymentGatewayError("شناسه پیگیری تراکنش از درگاه دریافت نشد")

        return PaymentRequestResult(
            track_id=str(track_id),
            redirect_url=self.client.get_start_pay_url(track_id),
            raw_response=response,
        )

    def verify_payment(self, order, params):
        track_id = params.get("trackId") or order.payment_track_id
        if not track_id:
            raise PaymentVerificationError("شناسه پیگیری تراکنش موجود نیست")

        # Sanity-check the orderId Zibal echoes back in the callback, when present.
        callback_order_id = params.get("orderId")
        if callback_order_id and callback_order_id != order.order_number:
            logger.warning(
                "Zibal callback orderId mismatch: expected=%s got=%s",
                order.order_number,
                callback_order_id,
            )

        response = self.client.verify_payment(track_id)
        result_code = response.get("result")

        if result_code in (self.RESULT_SUCCESS, self.RESULT_ALREADY_VERIFIED):
            reference_id = response.get("refNumber") or track_id
            return PaymentVerifyResult(
                success=True,
                reference_id=str(reference_id),
                raw_response=response,
            )

        message = self.RESULT_MESSAGES.get(
            result_code, response.get("message") or "پرداخت تایید نشد"
        )
        logger.warning(
            "Zibal verify_payment failed: order=%s result=%s",
            order.order_number,
            result_code,
        )
        return PaymentVerifyResult(
            success=False, reference_id=None, raw_response=response, message=message
        )


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


class PaymentService:
    """Entry point used by the ``orders`` views.

    Usage::

        service = PaymentService()
        redirect_url = service.initiate_payment(order, callback_url)
        ...
        success = service.verify_payment(order, request.GET)
    """

    def __init__(self):
        self.gateway = ZibalGateway()

    def initiate_payment(self, order, callback_url):
        """Create a transaction with Zibal and return the URL the user must
        be redirected to in order to pay."""
        from orders.models import Order, OrderStatusChoices

        with transaction.atomic():
            order = Order.objects.select_for_update().get(pk=order.pk)

            if not order.can_be_paid():
                raise PaymentError("این سفارش قابل پرداخت نیست")

            result = self.gateway.request_payment(order, callback_url)

            order.payment_gateway = self.gateway.name
            order.payment_track_id = result.track_id
            order.status = OrderStatusChoices.PROCESSING
            order.save(
                update_fields=[
                    "payment_gateway",
                    "payment_track_id",
                    "status",
                    "updated_date",
                ]
            )

        logger.info(
            "Payment initiated: order=%s gateway=%s track_id=%s",
            order.order_number,
            self.gateway.name,
            result.track_id,
        )
        return result.redirect_url

    def verify_payment(self, order, params):
        """Verify a transaction with Zibal and mark the order as paid on
        success. Idempotent: safe to call multiple times for the same
        order/callback (duplicate callback / duplicate verification
        protection)."""
        from orders.models import Order, OrderStatusChoices

        with transaction.atomic():
            order = Order.objects.select_for_update().get(pk=order.pk)

            # Duplicate callback protection: if this order was already
            # marked paid by a previous callback/verification, do not hit
            # the gateway's verify endpoint again - just report success.
            if order.is_paid:
                logger.info(
                    "Duplicate payment callback ignored, order already paid: order=%s",
                    order.order_number,
                )
                return True

            try:
                result = self.gateway.verify_payment(order, params)
            except PaymentError:
                raise
            except Exception as exc:  # noqa: BLE001 - convert to our own type
                logger.exception(
                    "Unexpected error verifying payment: order=%s", order.order_number
                )
                raise PaymentVerificationError("خطا در تایید پرداخت") from exc

            if result.success:
                order.mark_as_paid(result.reference_id)
                logger.info(
                    "Payment verified successfully: order=%s gateway=%s ref=%s",
                    order.order_number,
                    self.gateway.name,
                    result.reference_id,
                )
                return True

            order.status = OrderStatusChoices.FAILED
            order.save(update_fields=["status", "updated_date"])
            logger.warning(
                "Payment verification failed: order=%s gateway=%s message=%s",
                order.order_number,
                self.gateway.name,
                result.message,
            )
            return False
