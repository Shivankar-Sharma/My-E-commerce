import pandas as pd
from celery import shared_task
from django.db import transaction
from ..models import Product, Option, ImportJobs
from .base_service import BaseService
from math import isnan

CHUNK_SIZE = 7000


@shared_task(bind=True)
def import_product_task(self, import_job_id):
    import_job = ImportJobs.objects.get(pk=import_job_id)
    import_job.status = "running"
    import_job.save()

    try:
        df = pd.read_excel(import_job.file_path)
        df = df.where(df.notnull(), None)
        rows = df.to_dict("records")
        import_job.total_rows = len(df)
        import_job.save()

        option_map = {}
        update_product_fields = [
            field.attname
            for field in Product._meta.get_fields()
            if field.name
            not in (
                "id",
                "created_at",
                "updated_at",
                "upc",
                "product_code_other",
                "supplier_name",
            )
        ]

        products = []

        for row in rows:
            products.append(
                Product(
                    # upc=row["UPC"],
                    product_code_other=row["PRODUCT CODE"],
                    variant_name=row["VARIANT NAME"],
                    template_name=row["TEMPLATE NAME"],
                    style_ranking_id=get_create_options(
                        option_map, "STYLE RANKING", row["STYLE RANKING"]
                    ),
                    list_price=clean_decimal(row["LIST PRICE"]),
                    wholesale_price=clean_decimal(row["WHOLESALE PRICE"]),
                    current_price=clean_decimal(row["CURRENT PRICE"]),
                    manual=row["MD Discount (MD%)"],
                    cost_price_method_id=get_create_options(
                        option_map, "COST METHOD", row["COST METHOD"]
                    ),
                    price_method_id=get_create_options(
                        option_map, "SALES TYPE", row["SALES TYPE"]
                    ),
                    lifecycle_id=get_create_options(
                        option_map, "LIFECYCLE", row["LIFECYCLE"]
                    ),
                    age_range_id=get_create_options(
                        option_map, "AGE RANGE", row["AGE RANGE"]
                    ),
                    prebook=row["PREBOOK"] or False,
                    tax_code_id=get_create_options(
                        option_map, "TAX CODE", row["TAX CODE"]
                    ),
                    height=clean_decimal(row["HEIGHT"]),
                    length=clean_decimal(row["LENGTH"]),
                    width=clean_decimal(row["WIDTH"]),
                    weight=clean_decimal(row["WEIGHT"]),
                    dimension_uom_name_id=get_create_options(
                        option_map, "DIMENSIONS UOM", row["DIMENSIONS UOM"]
                    ),
                    weight_uom_name_id=get_create_options(
                        option_map, "WEIGHT UOM NAME", row["WEIGHT UOM NAME"]
                    ),
                    hs_code_id=get_create_options(
                        option_map, "HS CODES", row["HS CODES"]
                    ),
                    custom_description=row["CUSTOM DESCRIPTION"],
                    buyer_sku="SS-HR51",
                    nu_customer_group=row["NU CUSTOMER GROUPS"],
                    country_of_origin=row["COUNTRY OF ORIGIN"],
                )
            )

            if len(products) >= CHUNK_SIZE:
                Product.objects.bulk_create(
                    products,
                    batch_size=CHUNK_SIZE,
                    update_conflicts=True,
                    update_fields=update_product_fields,
                    unique_fields=["product_code_other"],
                )
                import_job.processed_rows += len(products)
                import_job.save(update_fields=["processed_rows"])
                products.clear()

        if products:
            Product.objects.bulk_create(
                products,
                batch_size=CHUNK_SIZE,
                update_conflicts=True,
                update_fields=update_product_fields,
                unique_fields=["product_code_other"],
            )
            import_job.processed_rows += len(products)
            import_job.save(update_fields=["processed_rows"])

        import_job.status = "finished"
        import_job.save()
    except Exception as e:
        import_job.status = "failed"
        import_job.errors = str(e)
        import_job.save()
        raise


def get_create_options(option_map, field_name, value):
    if not value:
        return None

    field_cache = option_map.setdefault(field_name, {})

    if value in field_cache:
        return field_cache[value]

    option = BaseService.set_option_data(field_name, value)
    option_id = option.pk if option else None

    field_cache[value] = option_id
    return option_id


def clean_decimal(val):
    if val is None:
        return None
    if isinstance(val, float) and isnan(val):
        return None
    if isinstance(val, str) and val.strip().lower() in {"nan", "n/a", "null", ""}:
        return None
    return val
