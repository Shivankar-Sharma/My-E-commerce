from django.db import models
from django.contrib.auth.models import User


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
    upc = models.CharField(max_length=11, unique=True)
    product_code_other = models.CharField(max_length=25, db_index=True, unique=True)
    variant_name = models.TextField()
    template_name = models.TextField()
    style_ranking = models.ForeignKey(
        "Option",
        on_delete=models.PROTECT,
        related_name="style_ranking_product",
        null=True,
        blank=True,
    )
    list_price = models.DecimalField(
        max_digits=4, decimal_places=2, null=True, blank=True
    )
    wholesale_price = models.DecimalField(
        max_digits=4, decimal_places=2, null=True, blank=True
    )
    current_price = models.DecimalField(
        max_digits=4, decimal_places=2, null=True, blank=True
    )
    manual = models.CharField(max_length=5)
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
    height = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    length = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    width = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    weight = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
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
    custom_description = models.TextField()
    supplier_name = models.ManyToManyField(
        "Option", related_name="supplier_name_product"
    )
    buyer_sku = models.CharField(max_length=10)
    nu_customer_group = models.CharField(max_length=10)
    country_of_origin = models.CharField(max_length=10)


class Option(models.Model):
    field_name = models.CharField(max_length=25)
    value = models.CharField(max_length=25)

    class Meta:
        db_table = "option_table"
        verbose_name = "Option"
        verbose_name_plural = "Options"
        unique_together = ("field_name", "value")

    def __str__(self):
        return f"{self.field_name}: {self.value}"
