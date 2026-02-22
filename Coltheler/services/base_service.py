from django.core.exceptions import ObjectDoesNotExist
from ..models import UserProfile, Product, Option, PoTemplate
from datetime import datetime


class BaseService:
    """
    A reusable base class for common operations.
    """

    @staticmethod
    def get_user_details(user_id):
        """
        safely get an object or None
        :param user_id:
        :return:
        """
        try:
            user = UserProfile.objects.get(user_id=user_id)

            if not user:
                return {}

            data = {
                "address1": user.address.split(";")[0] if user.address else "",
                "address2": (
                    user.address.split(";")[1]
                    if user.address and ";" in user.address
                    else ""
                ),
                "city": user.city,
                "state": user.state,
                "zipcode": user.zipcode,
                "phone": user.phone,
                "profile_pic": user.profile_pic,
            }
            return data
        except ObjectDoesNotExist:
            return {}

    @staticmethod
    def set_product_data(product_object, data):
        try:
            if not product_object.upc:
                product_object.upc = data.get("upc")
            if not product_object.product_code_other:
                product_object.product_code_other = data.get("product_code")
            product_object.variant_name = data.get("variant_name")
            product_object.template_name = data.get("template_name")
            product_object.style_ranking_id = data.get("style_ranking") or None
            product_object.list_price = data.get("list_price")
            product_object.wholesale_price = data.get("wholesale_price")
            product_object.current_price = data.get("current_price")
            product_object.manual = data.get("manual")
            prebook = data.get("prebook", False) == "True"
            product_object.prebook = prebook
            product_object.height = data.get("height")
            product_object.width = data.get("width")
            product_object.length = data.get("length")
            product_object.weight = data.get("weight")
            product_object.custom_description = data.get("custom_description")
            product_object.buyer_sku = data.get("buyer_sku")
            product_object.nu_customer_group = data.get("nu_customer_group")
            product_object.country_of_origin = data.get("country_of_origin")

        except Exception as e:
            return e

    @staticmethod
    def get_product_data(product_code):
        try:
            product = Product.objects.get(product_code=product_code)
            data = {
                "upc": product.upc,
                "product_code": product_code,
                "variant_name": product.variant_name,
                "template_name": product.template_name,
                "list_price": product.list_price,
                "wholesale_price": product.wholesale_price,
                "current_price": product.current_price,
                "manual": product.manual,
                "prebook": product.prebook,
                "height": product.height,
                "width": product.width,
                "length": product.length,
                "weight": product.weight,
                "custom_description": product.custom_description,
                "buyer_sku": product.buyer_sku,
                "country_of_origin": product.country_of_origin,
                "nu_customer_group": product.nu_customer_group,
            }
            return data
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def set_option_data(field_name, value):
        try:
            option_object, _ = Option.objects.get_or_create(
                field_name=field_name, value=value
            )
            return option_object
        except Exception as e:
            print(e)
            return None

    @staticmethod
    def get_po_references(row):
        reference_array = {}
        po_number = str(row["PO NUMBER"]).strip()
        factory_code = str(row["FACTORY CODE"]).strip()

        if not po_number or not factory_code:
            return reference_array

        reference_type = ["SHP", "PRE", "CON", "ADS", "PSS", "WHL", "RVN"]

        for ref_type in reference_type:
            if ref_type not in row:
                continue

            quantity = row[ref_type]
            reference_name = f"H-COTH-{po_number}-{ref_type}|{factory_code}"
            reference_array[reference_name] = {
                "name": reference_name,
                "quantity": quantity,
                "have_whl": True if ref_type == "WHL" else False,
            }

        return reference_array

    @staticmethod
    def set_po_template_data(po_template, data):
        try:

            def parse_bool(value):
                return str(value).lower() in {"true", "1", "yes", "on"}

            def parse_date(value):
                return datetime.strptime(value, "%Y-%m-%d").date() if value else None

            if not po_template.reference:
                po_template.reference = data.get("reference")
            if not po_template.sku:
                po_template.sku = data.get("sku")
            po_template.purchase_date = parse_date(data.get("purchase_date"))
            po_template.variant_name = data.get("variant_name")
            po_template.quantity = data.get("quantity") or 0
            po_template.unit_price = data.get("unit_price")
            po_template.warehouse = data.get("warehouse")
            po_template.delivery_date = parse_date(data.get("delivery_date"))
            po_template.style_ranking_id = data.get("style_ranking") or None
            po_template.reference_have_whl = parse_bool(data.get("reference_have_whl"))
            po_template.requested_shipping_date = parse_date(
                data.get("requested_shipping_date")
            )
            po_template.sample_po = parse_bool(data.get("sample_po"))
            po_template.gs1_indicator = parse_bool(data.get("gs1_indicator"))
            po_template.created_at = datetime.now()
            po_template.updated_at = datetime.now()
        except Exception as e:
            return e
