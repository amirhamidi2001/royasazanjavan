from cart.cart import CartSession


def cart_context(request):
    """
    Context processor to make cart available in all templates.

    Add this to settings.py:
    TEMPLATES = [
        {
            ...
            'OPTIONS': {
                'context_processors': [
                    ...
                    'cart.context_processors.cart_context',
                ],
            },
        },
    ]

    Usage in templates:
    - {{ cart_total_quantity }} : Total number of courses in cart
    - {{ cart_total_price }} : Total price of cart
    """
    cart = CartSession(request.session)

    return {
        "cart": cart,
        "cart_total_quantity": cart.get_total_quantity(),
        "cart_total_price": cart.get_total_payment_amount(),
    }
