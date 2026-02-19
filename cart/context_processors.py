from cart.cart import CartSession


def cart_context(request):
    """
    Context processor to make cart available in all templates.
    """
    cart = CartSession(request.session)

    return {
        "cart": cart,
        "cart_total_quantity": cart.get_total_quantity(),
        "cart_total_price": cart.get_total_payment_amount(),
    }
