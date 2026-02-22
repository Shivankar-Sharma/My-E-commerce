from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify
import os


def asset_upload_path(instance, filename):
    safe_name = os.path.basename(filename)
    date_path = timezone.now().strftime("%Y/%m/%d")
    user = getattr(instance, "uploaded_by", None)
    display_name = ""
    if user:
        full_name = (user.get_full_name() or "").strip()
        display_name = full_name or (user.username or "")
    normalized = slugify(display_name).replace("-", "_")
    user_folder = normalized or f"user_{instance.uploaded_by_id or 'unknown'}"
    return f"assets/{user_folder}/{date_path}/{safe_name}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    profile_pic = models.ImageField(upload_to="profile_pic", null=True, blank=True)
    address = models.CharField(max_length=120)
    city = models.CharField(max_length=20)
    state = models.CharField(max_length=20)
    zipcode = models.CharField(max_length=10)
    phone = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_profile"

    def __str__(self):
        return f"{self.user.username} Profile"


class Product(models.Model):
    upc = models.CharField(max_length=15, unique=True, null=True, blank=True)
    product_code_other = models.CharField(max_length=25, db_index=True, unique=True)
    variant_name = models.TextField(null=True, blank=True)
    template_name = models.TextField(null=True, blank=True)
    style_ranking = models.ForeignKey(
        "Option",
        on_delete=models.PROTECT,
        related_name="style_ranking_product",
        null=True,
        blank=True,
    )
    list_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    wholesale_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    current_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    manual = models.CharField(max_length=5, null=True, blank=True)
    cost_price_method = models.ForeignKey(
        "Option",
        on_delete=models.PROTECT,
        related_name="cost_price_method_product",
        null=True,
        blank=True,
    )
    price_method = models.ForeignKey(
        "Option",
        on_delete=models.PROTECT,
        related_name="price_method_product",
        null=True,
        blank=True,
    )
    lifecycle = models.ForeignKey(
        "Option",
        on_delete=models.PROTECT,
        related_name="lifecycle_product",
        null=True,
        blank=True,
    )
    age_range = models.ForeignKey(
        "Option",
        on_delete=models.PROTECT,
        related_name="age_range_product",
        null=True,
        blank=True,
    )
    prebook = models.BooleanField(default=False)
    tax_code = models.ForeignKey(
        "Option",
        on_delete=models.PROTECT,
        related_name="tax_code_product",
        null=True,
        blank=True,
    )
    height = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    length = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    width = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    dimension_uom_name = models.ForeignKey(
        "Option",
        on_delete=models.PROTECT,
        related_name="dimension_uom_name_product",
        null=True,
        blank=True,
    )
    weight_uom_name = models.ForeignKey(
        "Option",
        on_delete=models.PROTECT,
        related_name="weight_uom_name_product",
        null=True,
        blank=True,
    )
    hs_code = models.ForeignKey(
        "Option",
        on_delete=models.PROTECT,
        related_name="hs_code_products",
        null=True,
        blank=True,
    )
    custom_description = models.TextField(null=True, blank=True)
    supplier_name = models.ManyToManyField(
        "Option", related_name="supplier_name_product"
    )
    buyer_sku = models.CharField(max_length=10, null=True, blank=True)
    nu_customer_group = models.CharField(max_length=10, null=True, blank=True)
    country_of_origin = models.CharField(max_length=10, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Option(models.Model):
    field_name = models.CharField(max_length=25)
    value = models.CharField(max_length=25)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "option_table"
        verbose_name = "Option"
        verbose_name_plural = "Options"
        unique_together = ("field_name", "value")

    def __str__(self):
        return f"{self.field_name}: {self.value}"


class ImportJobs(models.Model):
    STATIC_CHOICES = (
        ("pending", "Pending"),
        ("running", "Running"),
        ("finished", "Finished"),
        ("failed", "Failed"),
    )

    file_path = models.CharField(max_length=255)
    total_rows = models.IntegerField(default=0)
    processed_rows = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATIC_CHOICES)
    errors = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class PoTemplate(models.Model):
    reference = models.CharField(max_length=50)
    purchase_date = models.DateField(null=True, blank=True)
    variant_name = models.TextField(null=True, blank=True)
    sku = models.CharField(max_length=25, null=True, blank=True, db_index=True)
    quantity = models.PositiveIntegerField(default=0, null=True, blank=True)
    unit_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    warehouse = models.CharField(max_length=50, null=True, blank=True)
    delivery_date = models.DateField(null=True, blank=True)
    style_ranking = models.ForeignKey(
        "Option",
        on_delete=models.PROTECT,
        related_name="style_ranking_po",
        null=True,
        blank=True,
    )
    reference_have_whl = models.BooleanField(default=False)
    requested_shipping_date = models.DateField(null=True, blank=True)
    sample_po = models.BooleanField(default=False)
    gs1_indicator = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "po_template_table"

    def __str__(self):
        return f"{self.reference} | {self.sku}"


class Gs1UploadTemplate(models.Model):
    action = models.CharField(max_length=15, null=True, blank=True)
    gs1_company_prefix = models.CharField(max_length=25, null=True, blank=True)
    gtin = models.OneToOneField(
        "MasterUpc",
        on_delete=models.PROTECT,
        related_name="gs1_product",
        null=True,
        blank=True,
    )
    packaging_level = models.CharField(max_length=15, null=True, blank=True)
    description = models.CharField(max_length=150, null=True, blank=True)
    desc_1_language = models.CharField(max_length=5, default="en")
    brand_name = models.CharField(max_length=50, null=True, blank=True)
    brand_1_language = models.CharField(max_length=5, default="en")
    is_variable = models.BooleanField(default=False)
    is_purchasable = models.BooleanField(default=False)
    sku = models.CharField(
        max_length=25, null=True, blank=True, db_index=True, unique=True
    )
    global_product_classification = models.CharField(
        max_length=15, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "gs1_upload_template_table"
        constraints = [
            models.UniqueConstraint(fields=["sku", "gtin"], name="unique_sku_gtin")
        ]

    def __str__(self):
        return f"{self.sku}"


class MasterUpc(models.Model):
    upc = models.CharField(max_length=15, unique=True)
    assigned_to = models.ForeignKey(
        "Gs1UploadTemplate",
        on_delete=models.PROTECT,
        related_name="upcs",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "master_upc"

    def __str__(self):
        return f"{self.upc}"


class Asset(models.Model):
    file = models.FileField(upload_to=asset_upload_path)
    uploaded_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="assets")
    original_name = models.CharField(max_length=255)
    relative_dir = models.CharField(max_length=255, blank=True, default="")
    size = models.BigIntegerField(default=0)
    content_type = models.CharField(max_length=150, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "asset_file"
        indexes = [
            models.Index(fields=["uploaded_by", "created_at"]),
            models.Index(fields=["relative_dir"]),
        ]

    def __str__(self):
        return self.original_name
