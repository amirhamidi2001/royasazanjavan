from django.contrib.contenttypes.models import ContentType
from courses.models import Course
from shop.models import Product
from cart.models import CartModel, CartItemModel


class CartSession:
    """
    Session-based cart management for multiple product types.
    Supports both Course and Product models using content type distinction.
    Each item can only be added once (quantity=1).
    """

    def __init__(self, session):
        self.session = session
        self._cart = self.session.setdefault("cart", {"items": []})

    def add_product(self, product_id, product_type="course"):
        """
        Add a course or product to cart.

        Args:
            product_id: ID of the product
            product_type: Type of product - 'course' or 'product'

        Returns:
            bool: True if item was added, False if already exists
        """
        # Validate product type
        if product_type not in ["course", "product"]:
            raise ValueError("product_type must be 'course' or 'product'")

        # Check if product already exists in cart
        for item in self._cart["items"]:
            if (
                str(product_id) == str(item["product_id"])
                and product_type == item["product_type"]
            ):
                # Item already in cart, do nothing
                return False

        # Verify product exists and is active
        if not self._verify_product_exists(product_id, product_type):
            return False

        # Add new item with quantity=1
        new_item = {
            "product_id": str(product_id),
            "product_type": product_type,
            "quantity": 1,
        }
        self._cart["items"].append(new_item)
        self.save()
        return True

    def update_product_quantity(self, product_id, product_type, quantity):
        """
        Update product quantity. For both courses and products, quantity is limited to 1.

        Args:
            product_id: ID of the product
            product_type: Type of product - 'course' or 'product'
            quantity: Desired quantity (will be forced to 1)
        """
        quantity = max(1, min(1, int(quantity)))  # Force quantity to be 1

        for item in self._cart["items"]:
            if (
                str(product_id) == str(item["product_id"])
                and product_type == item["product_type"]
            ):
                item["quantity"] = quantity
                break
        else:
            return
        self.save()

    def remove_product(self, product_id, product_type):
        """
        Remove an item from cart.

        Args:
            product_id: ID of the product
            product_type: Type of product - 'course' or 'product'
        """
        for item in self._cart["items"]:
            if (
                str(product_id) == str(item["product_id"])
                and product_type == item["product_type"]
            ):
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
        Get cart items with full product objects and calculated prices.
        Returns list of items with product_obj, product_type, and total_price.

        Returns:
            list: List of dictionaries containing:
                - product_id: ID of the product
                - product_type: Type of product ('course' or 'product')
                - quantity: Quantity (always 1)
                - product_obj: Full Course or Product object
                - total_price: Final calculated price
        """
        cart_items = []
        invalid_items = []

        for item in self._cart["items"]:
            try:
                product_type = item.get("product_type", "course")
                product_id = item["product_id"]

                # Get product object based on type
                if product_type == "course":
                    product_obj = Course.objects.get(id=product_id, is_active=True)
                    # For courses, use the price field directly
                    price = product_obj.price
                elif product_type == "product":
                    product_obj = Product.objects.get(id=product_id, is_active=True)
                    # For products, use get_final_price() method
                    price = product_obj.get_final_price()
                else:
                    # Unknown product type, skip
                    invalid_items.append(item)
                    continue

                item_data = {
                    "product_id": product_id,
                    "product_type": product_type,
                    "quantity": item["quantity"],
                    "product_obj": product_obj,
                    "total_price": item["quantity"] * price,
                }
                cart_items.append(item_data)

            except (Course.DoesNotExist, Product.DoesNotExist):
                # Remove invalid product from cart
                invalid_items.append(item)

        # Clean up invalid items
        if invalid_items:
            for invalid_item in invalid_items:
                self._cart["items"].remove(invalid_item)
            self.save()

        return cart_items

    def get_total_payment_amount(self):
        """Calculate total payment amount for all items in cart."""
        items = self.get_cart_items()
        return sum(item["total_price"] for item in items)

    def get_total_quantity(self):
        """Get total number of items in cart."""
        return len(self._cart["items"])

    def is_product_in_cart(self, product_id, product_type="course"):
        """
        Check if a product is already in the cart.

        Args:
            product_id: ID of the product
            product_type: Type of product - 'course' or 'product'

        Returns:
            bool: True if product is in cart
        """
        return any(
            str(product_id) == str(item["product_id"])
            and product_type == item.get("product_type", "course")
            for item in self._cart["items"]
        )

    def is_course_in_cart(self, course_id):
        """Legacy method for backward compatibility. Check if a course is in cart."""
        return self.is_product_in_cart(course_id, "course")

    def save(self):
        """Mark session as modified to ensure it's saved."""
        self.session.modified = True

    def _verify_product_exists(self, product_id, product_type):
        """
        Verify that a product exists and is active.

        Args:
            product_id: ID of the product
            product_type: Type of product - 'course' or 'product'

        Returns:
            bool: True if product exists and is active
        """
        try:
            if product_type == "course":
                Course.objects.get(id=product_id, is_active=True)
            elif product_type == "product":
                Product.objects.get(id=product_id, is_active=True)
            else:
                return False
            return True
        except (Course.DoesNotExist, Product.DoesNotExist):
            return False

    def sync_cart_items_from_db(self, user):
        """
        Sync cart items from database when user logs in.
        Merge database cart with session cart.
        """
        cart, created = CartModel.objects.get_or_create(user=user)
        cart_items = CartItemModel.objects.filter(cart=cart)

        # Load items from database into session
        for cart_item in cart_items:
            # Get product type from ContentType
            product_type = cart_item.content_type.model
            product_id = cart_item.object_id

            # Check if item already exists in session
            found = False
            for item in self._cart["items"]:
                if str(product_id) == str(
                    item["product_id"]
                ) and product_type == item.get("product_type", "course"):
                    # Item exists in both, keep session quantity (always 1)
                    cart_item.quantity = 1
                    cart_item.save()
                    found = True
                    break

            if not found and cart_item.is_active():
                # Item only in database, add to session
                new_item = {
                    "product_id": str(product_id),
                    "product_type": product_type,
                    "quantity": 1,
                }
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
                product_type = item.get("product_type", "course")
                product_id = item["product_id"]

                # Get the appropriate model and content type
                if product_type == "course":
                    product_obj = Course.objects.get(id=product_id, is_active=True)
                    content_type = ContentType.objects.get_for_model(Course)
                elif product_type == "product":
                    product_obj = Product.objects.get(id=product_id, is_active=True)
                    content_type = ContentType.objects.get_for_model(Product)
                else:
                    continue

                # Create or update cart item
                cart_item, created = CartItemModel.objects.get_or_create(
                    cart=cart, content_type=content_type, object_id=product_obj.id
                )
                cart_item.quantity = 1  # Always 1
                cart_item.save()

            except (Course.DoesNotExist, Product.DoesNotExist):
                # Invalid product, skip
                continue

        # Remove items from database that are not in session
        session_items = [
            (item.get("product_type", "course"), item["product_id"])
            for item in self._cart["items"]
        ]

        # Delete items not in session
        for db_item in CartItemModel.objects.filter(cart=cart):
            item_type = db_item.content_type.model
            item_id = str(db_item.object_id)
            if (item_type, item_id) not in session_items:
                db_item.delete()
