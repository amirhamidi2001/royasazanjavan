from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from cart.cart import CartSession


@receiver(user_logged_in)
def sync_cart_on_login(sender, request, user, **kwargs):
    """
    Automatically sync cart from database when user logs in.
    This merges any items in the session cart with items in the database.
    """
    cart = CartSession(request.session)
    cart.sync_cart_items_from_db(user)
