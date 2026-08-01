"""
Payment gateway integration package.

This package isolates all payment-gateway concerns (Zibal, used in both
development and production) from the rest of the business logic. Views
should only ever talk to ``payments.services``.
"""
