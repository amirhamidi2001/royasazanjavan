from courses.models import Course
from cart.models import CartModel, CartItemModel


class CartSession:
    """
    Session-based cart management for educational courses.
    Each course can only be added once (quantity=1).
    """

    def __init__(self, session):
        self.session = session
        self._cart = self.session.setdefault("cart", {"items": []})

    def add_product(self, product_id):
        """
        Add a course to cart. For educational courses, only one instance per course is allowed.
        If course already exists in cart, do nothing.
        """
        # Check if product already exists in cart
        for item in self._cart["items"]:
            if str(product_id) == str(item["product_id"]):
                # Course already in cart, do nothing
                return False

        # Add new course with quantity=1
        new_item = {"product_id": str(product_id), "quantity": 1}
        self._cart["items"].append(new_item)
        self.save()
        return True

    def update_product_quantity(self, product_id, quantity):
        """
        Update product quantity. For educational courses, this is typically not used.
        Kept for compatibility but limits quantity to 1.
        """
        quantity = max(1, min(1, int(quantity)))  # Force quantity to be 1

        for item in self._cart["items"]:
            if str(product_id) == str(item["product_id"]):
                item["quantity"] = quantity
                break
        else:
            return
        self.save()

    def remove_product(self, product_id):
        """Remove a course from cart."""
        for item in self._cart["items"]:
            if str(product_id) == str(item["product_id"]):
                self._cart["items"].remove(item)
                break
        else:
            return
        self.save()

    def clear(self):
        """Clear all items from cart."""
        self._cart = self.session["cart"] = {"items": []}
        self.save()

    def get_cart_dict(self):
        """Get raw cart dictionary."""
        return self._cart

    def get_cart_items(self):
        """
        Get cart items with full course objects and calculated prices.
        Returns list of items with course_obj and total_price.
        """
        cart_items = []
        for item in self._cart["items"]:
            try:
                course_obj = Course.objects.get(id=item["product_id"], is_active=True)
                item_data = {
                    "product_id": item["product_id"],
                    "quantity": item["quantity"],
                    "course_obj": course_obj,
                    "total_price": item["quantity"] * course_obj.price,
                }
                cart_items.append(item_data)
            except Course.DoesNotExist:
                # Remove invalid course from cart
                self._cart["items"].remove(item)
                self.save()

        return cart_items

    def get_total_payment_amount(self):
        """Calculate total payment amount for all items in cart."""
        items = self.get_cart_items()
        return sum(item["total_price"] for item in items)

    def get_total_quantity(self):
        """Get total number of items (courses) in cart."""
        return len(self._cart["items"])

    def is_course_in_cart(self, course_id):
        """Check if a course is already in the cart."""
        return any(
            str(course_id) == str(item["product_id"]) for item in self._cart["items"]
        )

    def save(self):
        """Mark session as modified to ensure it's saved."""
        self.session.modified = True

    def sync_cart_items_from_db(self, user):
        """
        Sync cart items from database when user logs in.
        Merge database cart with session cart.
        """
        cart, created = CartModel.objects.get_or_create(user=user)
        cart_items = CartItemModel.objects.filter(cart=cart)

        # Load items from database into session
        for cart_item in cart_items:
            found = False
            for item in self._cart["items"]:
                if str(cart_item.product.id) == str(item["product_id"]):
                    # Item exists in both, keep session quantity (always 1 for courses)
                    cart_item.quantity = 1
                    cart_item.save()
                    found = True
                    break

            if not found:
                # Item only in database, add to session
                new_item = {"product_id": str(cart_item.product.id), "quantity": 1}
                self._cart["items"].append(new_item)

        # Merge session cart into database
        self.merge_session_cart_in_db(user)
        self.save()

    def merge_session_cart_in_db(self, user):
        """
        Merge session cart items into database cart.
        Remove items from database that are not in session.
        """
        cart, created = CartModel.objects.get_or_create(user=user)

        # Add/update session items in database
        for item in self._cart["items"]:
            try:
                course_obj = Course.objects.get(id=item["product_id"], is_active=True)
                cart_item, created = CartItemModel.objects.get_or_create(
                    cart=cart, product=course_obj
                )
                cart_item.quantity = 1  # Always 1 for courses
                cart_item.save()
            except Course.DoesNotExist:
                # Invalid course, skip
                continue

        # Remove items from database that are not in session
        session_product_ids = [item["product_id"] for item in self._cart["items"]]
        CartItemModel.objects.filter(cart=cart).exclude(
            product__id__in=session_product_ids
        ).delete()
