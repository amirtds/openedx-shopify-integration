import json
import unittest
from unittest.mock import Mock
from random import randint
from os import environ

import functions


class ProductCreatorTests(unittest.TestCase):
    def setUp(self):
        functions.shopify_secret = environ.get("shopify_secret", "")
        functions.shopify_store_url = "https://amirtds.myshopify.com"
        functions.environment = "test"
        functions.shopify_store_admin_api = environ.get("shopify_store_admin_api", "")
        functions.tahoe_sites = "https://cody.staging-tahoe.appsembler.com,https://matthew-staging.staging-tahoe.appsembler.com,https://amirtadrisi.staging-tahoe.appsembler.com"
        functions.tahoe_courses_api = "/api/courses/v1/courses/"
        self.shopify_products = [
            {
                "product_title": "Unit test demo course {}".format(
                    str(randint(1000, 99999))
                ),
                "product_description": "Test course made during testing",
                "product_sku": "course-v1:amirtadrisi+unittest+{}".format(
                    str(randint(1000, 99999))
                ),
                "product_image": "https://www.vitoshacademy.com/wp-content/uploads/2016/05/UnitTests-300x225.jpg",
                "product_tag": "https://amirtds.myshopify.com",
            }
        ]

    def test_create_non_existing_product(self):
        result = functions.create_shopify_products(self.shopify_products)
        self.assertEqual(
            result.response[0].decode(),
            "1 Product(s) got created"
        )

    def test_create_existing_product(self):
        self.shopify_products[0]["product_sku"] = "course-v1:amirtadrisi+demo101+2020"
        result = functions.create_shopify_products(self.shopify_products)
        self.assertEqual(
            result.response[0].decode(),
            "0 Product(s) got created"
        )


if __name__ == "__main__":
    unittest.main()
