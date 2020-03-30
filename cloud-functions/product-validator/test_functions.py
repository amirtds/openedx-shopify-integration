import json
import unittest
from unittest.mock import Mock
from os import environ

import functions


class ProductValidatorTests(unittest.TestCase):
    # create sample json data
    def setUp(self):
        functions.shopify_secret = environ.get("shopify_secret", "")
        functions.shopify_store_url = "https://amirtds.myshopify.com"
        functions.environment = "test"
        functions.shopify_store_admin_api = environ.get("shopify_store_admin_api", "")
        functions.tahoe_sites = "https://cody.staging-tahoe.appsembler.com,https://matthew-staging.staging-tahoe.appsembler.com,https://amirtadrisi.staging-tahoe.appsembler.com".split(
            ","
        )
        functions.tahoe_courses_api = "/api/courses/v1/courses/"
        self.json_data = {
            "id": 788032119674292922,
            "title": "Example T-Shirt",
            "body_html": None,
            "vendor": "Acme",
            "product_type": "Shirts",
            "created_at": None,
            "handle": "example-t-shirt",
            "updated_at": "2020-03-27T20:31:35-04:00",
            "published_at": "2020-03-27T20:31:35-04:00",
            "template_suffix": None,
            "published_scope": "web",
            "tags": "example, mens, t-shirt",
            "admin_graphql_api_id": "gid://shopify/Product/788032119674292922",
            "variants": [
                {
                    "id": 642667041472713922,
                    "product_id": 788032119674292922,
                    "title": "",
                    "price": "19.99",
                    "sku": "course-v1:amirtadrisi+demo101+2020",
                    "position": 0,
                    "inventory_policy": "deny",
                    "compare_at_price": "24.99",
                    "fulfillment_service": "manual",
                    "inventory_management": "shopify",
                    "option1": "Small",
                    "option2": None,
                    "option3": None,
                    "created_at": None,
                    "updated_at": None,
                    "taxable": True,
                    "barcode": None,
                    "grams": 200,
                    "image_id": None,
                    "weight": 200.0,
                    "weight_unit": "g",
                    "inventory_item_id": None,
                    "inventory_quantity": 75,
                    "old_inventory_quantity": 75,
                    "requires_shipping": True,
                    "admin_graphql_api_id": "gid://shopify/ProductVariant/642667041472713922",
                },
                {
                    "id": 757650484644203962,
                    "product_id": 788032119674292922,
                    "title": "",
                    "price": "19.99",
                    "sku": "course-v1:amirtadrisi+demo101+2020",
                    "position": 0,
                    "inventory_policy": "deny",
                    "compare_at_price": "24.99",
                    "fulfillment_service": "manual",
                    "inventory_management": "shopify",
                    "option1": "Medium",
                    "option2": None,
                    "option3": None,
                    "created_at": None,
                    "updated_at": None,
                    "taxable": True,
                    "barcode": None,
                    "grams": 200,
                    "image_id": None,
                    "weight": 200.0,
                    "weight_unit": "g",
                    "inventory_item_id": None,
                    "inventory_quantity": 50,
                    "old_inventory_quantity": 50,
                    "requires_shipping": True,
                    "admin_graphql_api_id": "gid://shopify/ProductVariant/757650484644203962",
                },
            ],
            "options": [
                {
                    "id": 527050010214937811,
                    "product_id": 788032119674292922,
                    "name": "Title",
                    "position": 1,
                    "values": ["Small", "Medium"],
                }
            ],
            "images": [
                {
                    "id": 539438707724640965,
                    "product_id": 788032119674292922,
                    "position": 0,
                    "created_at": None,
                    "updated_at": None,
                    "alt": None,
                    "width": 323,
                    "height": 434,
                    "src": "//cdn.shopify.com/s/assets/shopify_shirt-39bb555874ecaeed0a1170417d58bbcf792f7ceb56acfe758384f788710ba635.png",
                    "variant_ids": [],
                    "admin_graphql_api_id": "gid://shopify/ProductImage/539438707724640965",
                }
            ],
            "image": None,
        }
        self.request = Mock()
        self.request.get_json.return_value = self.json_data
        self.request.headers = {
            "X-Shopify-Hmac-SHA256": "U6JwHo6q6baLlz1WW6ZzwBeA6epmsx5dHX/GU97rj4Y="
        }

    def test_create_invalid_product(self):
        self.request.get_json()["variants"][0]["sku"] = "invalid course id"
        result = functions.shopify_product_validator(self.request)
        self.assertEqual(result.response[0].decode(), "SKU wasn't valid")

    def test_create_valid_product(self):
        result = functions.shopify_product_validator(self.request)
        self.assertEqual(result.response[0].decode(), "SKU is valid")

    def test_update_invalid_product(self):
        self.json_data = {
            "id": 788032119674292922,
            "title": "Example T-Shirt",
            "body_html": None,
            "vendor": "Acme",
            "product_type": "Shirts",
            "created_at": None,
            "handle": "example-t-shirt",
            "updated_at": "2020-03-27T21:11:09-04:00",
            "published_at": "2020-03-27T21:11:09-04:00",
            "template_suffix": None,
            "published_scope": "web",
            "tags": "example, mens, t-shirt",
            "admin_graphql_api_id": "gid://shopify/Product/788032119674292922",
            "variants": [
                {
                    "id": 642667041472713922,
                    "product_id": 788032119674292922,
                    "title": "",
                    "price": "19.99",
                    "sku": "example-shirt-s",
                    "position": 0,
                    "inventory_policy": "deny",
                    "compare_at_price": "24.99",
                    "fulfillment_service": "manual",
                    "inventory_management": "shopify",
                    "option1": "Small",
                    "option2": None,
                    "option3": None,
                    "created_at": None,
                    "updated_at": None,
                    "taxable": True,
                    "barcode": None,
                    "grams": 200,
                    "image_id": None,
                    "weight": 200.0,
                    "weight_unit": "g",
                    "inventory_item_id": None,
                    "inventory_quantity": 75,
                    "old_inventory_quantity": 75,
                    "requires_shipping": True,
                    "admin_graphql_api_id": "gid://shopify/ProductVariant/642667041472713922",
                },
                {
                    "id": 757650484644203962,
                    "product_id": 788032119674292922,
                    "title": "",
                    "price": "19.99",
                    "sku": "example-shirt-m",
                    "position": 0,
                    "inventory_policy": "deny",
                    "compare_at_price": "24.99",
                    "fulfillment_service": "manual",
                    "inventory_management": "shopify",
                    "option1": "Medium",
                    "option2": None,
                    "option3": None,
                    "created_at": None,
                    "updated_at": None,
                    "taxable": True,
                    "barcode": None,
                    "grams": 200,
                    "image_id": None,
                    "weight": 200.0,
                    "weight_unit": "g",
                    "inventory_item_id": None,
                    "inventory_quantity": 50,
                    "old_inventory_quantity": 50,
                    "requires_shipping": True,
                    "admin_graphql_api_id": "gid://shopify/ProductVariant/757650484644203962",
                },
            ],
            "options": [
                {
                    "id": 527050010214937811,
                    "product_id": 788032119674292922,
                    "name": "Title",
                    "position": 1,
                    "values": ["Small", "Medium"],
                }
            ],
            "images": [
                {
                    "id": 539438707724640965,
                    "product_id": 788032119674292922,
                    "position": 0,
                    "created_at": None,
                    "updated_at": None,
                    "alt": None,
                    "width": 323,
                    "height": 434,
                    "src": "//cdn.shopify.com/s/assets/shopify_shirt-39bb555874ecaeed0a1170417d58bbcf792f7ceb56acfe758384f788710ba635.png",
                    "variant_ids": [],
                    "admin_graphql_api_id": "gid://shopify/ProductImage/539438707724640965",
                }
            ],
            "image": None,
        }
        self.request.headers = {
            "X-Shopify-Hmac-SHA256": "0EoKBiPkKSGVX9vH4CheMh2obFaLd9WRuGJjuefo8VY="
        }
        self.request.get_json()["variants"][0]["sku"] = "invalid course id"
        result = functions.shopify_product_validator(self.request)
        self.assertEqual(result.response[0].decode(), "SKU wasn't valid")


if __name__ == "__main__":
    unittest.main()
