from django.views.generic import ListView, DetailView
from django.db.models import Q
from decimal import Decimal
from .models import Product, Category
from .forms import ProductFilterForm


class ProductListView(ListView):
    """
    Display list of products with filtering, searching, and pagination
    """

    model = Product
    template_name = "shop/product_list.html"
    context_object_name = "products"
    paginate_by = 12

    def get_queryset(self):
        """
        Filter products based on search, category, price range, and type
        """
        queryset = Product.objects.filter(is_active=True).select_related("category")

        # Search by title or description
        search_query = self.request.GET.get("search", "").strip()
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query)
                | Q(description__icontains=search_query)
                | Q(short_description__icontains=search_query)
            )

        # Filter by category (including subcategories)
        category_slug = self.request.GET.get("category", "").strip()
        if category_slug:
            try:
                category = Category.objects.get(slug=category_slug, is_active=True)
                # Get category and all its children
                categories = [category] + category.get_all_children()
                queryset = queryset.filter(category__in=categories)
            except Category.DoesNotExist:
                pass

        # Filter by product type
        product_type = self.request.GET.get("type", "").strip()
        if product_type and product_type in dict(Product.PRODUCT_TYPE_CHOICES):
            queryset = queryset.filter(product_type=product_type)

        # Filter by price range
        min_price = self.request.GET.get("min_price", "").strip()
        max_price = self.request.GET.get("max_price", "").strip()

        if min_price:
            try:
                min_price_decimal = Decimal(min_price)
                queryset = queryset.filter(price__gte=min_price_decimal)
            except (ValueError, TypeError):
                pass

        if max_price:
            try:
                max_price_decimal = Decimal(max_price)
                queryset = queryset.filter(price__lte=max_price_decimal)
            except (ValueError, TypeError):
                pass

        # Filter free products
        is_free = self.request.GET.get("is_free", "").strip()
        if is_free == "true":
            queryset = queryset.filter(is_free=True)

        # Sorting
        sort_by = self.request.GET.get("sort", "-created_at")
        valid_sort_options = [
            "price",
            "-price",
            "title",
            "-title",
            "created_at",
            "-created_at",
        ]
        if sort_by in valid_sort_options:
            queryset = queryset.order_by(sort_by)

        return queryset

    def get_context_data(self, **kwargs):
        """
        Add extra context for filters and categories
        """
        context = super().get_context_data(**kwargs)

        # Add filter form
        context["filter_form"] = ProductFilterForm(self.request.GET)

        # Add all categories with their subcategories
        context["categories"] = Category.objects.filter(
            is_active=True, parent=None
        ).prefetch_related("subcategories")

        # Add current filters for display
        context["current_search"] = self.request.GET.get("search", "")
        context["current_category"] = self.request.GET.get("category", "")
        context["current_type"] = self.request.GET.get("type", "")
        context["current_sort"] = self.request.GET.get("sort", "-created_at")

        # Product types for filter
        context["product_types"] = Product.PRODUCT_TYPE_CHOICES

        # Pagination query string
        query_params = self.request.GET.copy()
        if "page" in query_params:
            query_params.pop("page")
        context["query_string"] = query_params.urlencode()

        return context


class ProductDetailView(DetailView):
    """
    Display detailed information about a single product
    """

    model = Product
    template_name = "shop/product_detail.html"
    context_object_name = "product"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        """
        Only show active products
        """
        return Product.objects.filter(is_active=True).select_related("category")

    def get_context_data(self, **kwargs):
        """
        Add related products and features
        """
        context = super().get_context_data(**kwargs)
        product = self.object

        # Get product features
        context["features"] = product.features.all()

        # Get related products (same category, excluding current product)
        if product.category:
            context["related_products"] = Product.objects.filter(
                category=product.category, is_active=True
            ).exclude(id=product.id)[:4]
        else:
            context["related_products"] = Product.objects.filter(
                is_active=True
            ).exclude(id=product.id)[:4]

        return context
