import json
import unittest
from unittest.mock import Mock
from random import randint
from os import environ

import functions


class SuccessfullPurchaseTests(unittest.TestCase):
    def setUp(self):
        functions.shopify_secret = environ.get("shopify_secret", "")
        functions.shopify_store_url = "https://amirtds.myshopify.com"
        functions.environment = "test"
        functions.shopify_store_admin_api = environ.get("shopify_store_admin_api", "")
        functions.tahoe_sites = "https://cody.staging-tahoe.appsembler.com,https://matthew-staging.staging-tahoe.appsembler.com,https://amirtadrisi.staging-tahoe.appsembler.com"
        functions.tahoe_courses_api = "/api/courses/v1/courses/"
        functions.tahoe_registration_api = "/tahoe/api/v1/registrations/"
        functions.tahoe_enrollment_api = "/tahoe/api/v1/enrollments/"
        functions.tahoe_users_api = "/tahoe/api/v1/users/"
        functions.tahoe_sites_tokens = environ.get("tahoe_sites_tokens", "")
        self.request_json = {
            "id": 820982911946154508,
            "email": "jon@doe.ca",
            "closed_at": None,
            "created_at": "2020-03-27T13:01:19-04:00",
            "updated_at": "2020-03-27T13:01:19-04:00",
            "number": 234,
            "note": None,
            "token": "123456abcd",
            "gateway": None,
            "test": True,
            "total_price": "5.00",
            "subtotal_price": "-5.00",
            "total_weight": 0,
            "total_tax": "0.00",
            "taxes_included": False,
            "currency": "USD",
            "financial_status": "paid",
            "confirmed": False,
            "total_discounts": "5.00",
            "total_line_items_price": "0.00",
            "cart_token": None,
            "buyer_accepts_marketing": True,
            "name": "#9999",
            "referring_site": None,
            "landing_site": None,
            "cancelled_at": "2020-03-27T13:01:19-04:00",
            "cancel_reason": "customer",
            "total_price_usd": None,
            "checkout_token": None,
            "reference": None,
            "user_id": None,
            "location_id": None,
            "source_identifier": None,
            "source_url": None,
            "processed_at": None,
            "device_id": None,
            "phone": None,
            "customer_locale": "en",
            "app_id": None,
            "browser_ip": None,
            "landing_site_ref": None,
            "order_number": 1234,
            "discount_applications": [
                {
                    "type": "manual",
                    "value": "5.0",
                    "value_type": "fixed_amount",
                    "allocation_method": "one",
                    "target_selection": "explicit",
                    "target_type": "line_item",
                    "description": "Discount",
                    "title": "Discount",
                }
            ],
            "discount_codes": [],
            "note_attributes": [],
            "payment_gateway_names": ["visa", "bogus"],
            "processing_method": "",
            "checkout_id": None,
            "source_name": "web",
            "fulfillment_status": "pending",
            "tax_lines": [],
            "tags": "https://amirtds.myshopify.com",
            "contact_email": "jon@doe.ca",
            "order_status_url": "https://amirtds.myshopify.com/28323282989/orders/123456abcd/authenticate?key=abcdefg",
            "presentment_currency": "USD",
            "total_line_items_price_set": {
                "shop_money": {"amount": "0.00", "currency_code": "USD"},
                "presentment_money": {"amount": "0.00", "currency_code": "USD"},
            },
            "total_discounts_set": {
                "shop_money": {"amount": "5.00", "currency_code": "USD"},
                "presentment_money": {"amount": "5.00", "currency_code": "USD"},
            },
            "total_shipping_price_set": {
                "shop_money": {"amount": "10.00", "currency_code": "USD"},
                "presentment_money": {"amount": "10.00", "currency_code": "USD"},
            },
            "subtotal_price_set": {
                "shop_money": {"amount": "-5.00", "currency_code": "USD"},
                "presentment_money": {"amount": "-5.00", "currency_code": "USD"},
            },
            "total_price_set": {
                "shop_money": {"amount": "5.00", "currency_code": "USD"},
                "presentment_money": {"amount": "5.00", "currency_code": "USD"},
            },
            "total_tax_set": {
                "shop_money": {"amount": "0.00", "currency_code": "USD"},
                "presentment_money": {"amount": "0.00", "currency_code": "USD"},
            },
            "line_items": [
                {
                    "id": 866550311766439020,
                    "variant_id": 33426620022829,
                    "title": "Demo course",
                    "quantity": 1,
                    "sku": "course-v1:amirtadrisi+demo101+2020",
                    "variant_title": None,
                    "vendor": None,
                    "fulfillment_service": "manual",
                    "product_id": 4814921662509,
                    "requires_shipping": True,
                    "taxable": True,
                    "gift_card": False,
                    "name": "Demo course",
                    "variant_inventory_management": None,
                    "properties": [],
                    "product_exists": True,
                    "fulfillable_quantity": 1,
                    "grams": 0,
                    "price": "0.00",
                    "total_discount": "0.00",
                    "fulfillment_status": None,
                    "price_set": {
                        "shop_money": {"amount": "0.00", "currency_code": "USD"},
                        "presentment_money": {"amount": "0.00", "currency_code": "USD"},
                    },
                    "total_discount_set": {
                        "shop_money": {"amount": "0.00", "currency_code": "USD"},
                        "presentment_money": {"amount": "0.00", "currency_code": "USD"},
                    },
                    "discount_allocations": [],
                    "admin_graphql_api_id": "gid://shopify/LineItem/866550311766439020",
                    "tax_lines": [],
                },
                {
                    "id": 141249953214522974,
                    "variant_id": 33426620022829,
                    "title": "Demo course",
                    "quantity": 1,
                    "sku": "course-v1:amirtadrisi+demo101+2020",
                    "variant_title": None,
                    "vendor": None,
                    "fulfillment_service": "manual",
                    "product_id": 4814921662509,
                    "requires_shipping": True,
                    "taxable": True,
                    "gift_card": False,
                    "name": "Demo course",
                    "variant_inventory_management": None,
                    "properties": [],
                    "product_exists": True,
                    "fulfillable_quantity": 1,
                    "grams": 0,
                    "price": "0.00",
                    "total_discount": "5.00",
                    "fulfillment_status": None,
                    "price_set": {
                        "shop_money": {"amount": "0.00", "currency_code": "USD"},
                        "presentment_money": {"amount": "0.00", "currency_code": "USD"},
                    },
                    "total_discount_set": {
                        "shop_money": {"amount": "5.00", "currency_code": "USD"},
                        "presentment_money": {"amount": "5.00", "currency_code": "USD"},
                    },
                    "discount_allocations": [
                        {
                            "amount": "5.00",
                            "discount_application_index": 0,
                            "amount_set": {
                                "shop_money": {
                                    "amount": "5.00",
                                    "currency_code": "USD",
                                },
                                "presentment_money": {
                                    "amount": "5.00",
                                    "currency_code": "USD",
                                },
                            },
                        }
                    ],
                    "admin_graphql_api_id": "gid://shopify/LineItem/141249953214522974",
                    "tax_lines": [],
                },
            ],
            "fulfillments": [],
            "refunds": [],
            "total_tip_received": "0.0",
            "admin_graphql_api_id": "gid://shopify/Order/820982911946154508",
            "shipping_lines": [
                {
                    "id": 271878346596884015,
                    "title": "Generic Shipping",
                    "price": "10.00",
                    "code": None,
                    "source": "shopify",
                    "phone": None,
                    "requested_fulfillment_service_id": None,
                    "delivery_category": None,
                    "carrier_identifier": None,
                    "discounted_price": "10.00",
                    "price_set": {
                        "shop_money": {"amount": "10.00", "currency_code": "USD"},
                        "presentment_money": {
                            "amount": "10.00",
                            "currency_code": "USD",
                        },
                    },
                    "discounted_price_set": {
                        "shop_money": {"amount": "10.00", "currency_code": "USD"},
                        "presentment_money": {
                            "amount": "10.00",
                            "currency_code": "USD",
                        },
                    },
                    "discount_allocations": [],
                    "tax_lines": [],
                }
            ],
            "billing_address": {
                "first_name": "Bob",
                "address1": "123 Billing Street",
                "phone": "555-555-BILL",
                "city": "Billtown",
                "zip": "K2P0B0",
                "province": "Kentucky",
                "country": "United States",
                "last_name": "Biller",
                "address2": None,
                "company": "My Company",
                "latitude": None,
                "longitude": None,
                "name": "Bob Biller",
                "country_code": "US",
                "province_code": "KY",
            },
            "shipping_address": {
                "first_name": "Steve",
                "address1": "123 Shipping Street",
                "phone": "555-555-SHIP",
                "city": "Shippington",
                "zip": "40003",
                "province": "Kentucky",
                "country": "United States",
                "last_name": "Shipper",
                "address2": None,
                "company": "Shipping Company",
                "latitude": None,
                "longitude": None,
                "name": "Steve Shipper",
                "country_code": "US",
                "province_code": "KY",
            },
            "customer": {
                "id": 115310627314723954,
                "email": "john@test.com",
                "accepts_marketing": False,
                "created_at": None,
                "updated_at": None,
                "first_name": "John",
                "last_name": "Smith",
                "orders_count": 0,
                "state": "disabled",
                "total_spent": "0.00",
                "last_order_id": None,
                "note": None,
                "verified_email": True,
                "multipass_identifier": None,
                "tax_exempt": False,
                "phone": None,
                "tags": "https://amirtds.myshopify.com",
                "last_order_name": None,
                "currency": "USD",
                "accepts_marketing_updated_at": None,
                "marketing_opt_in_level": None,
                "admin_graphql_api_id": "gid://shopify/Customer/115310627314723954",
                "default_address": {
                    "id": 715243470612851245,
                    "customer_id": 115310627314723954,
                    "first_name": None,
                    "last_name": None,
                    "company": None,
                    "address1": "123 Elm St.",
                    "address2": None,
                    "city": "Ottawa",
                    "province": "Ontario",
                    "country": "Canada",
                    "zip": "K2H7A8",
                    "phone": "123-123-1234",
                    "name": "",
                    "province_code": "ON",
                    "country_code": "CA",
                    "country_name": "Canada",
                    "default": True,
                },
            },
        }
        self.request = Mock()
        self.request.get_json.return_value = self.request_json
        self.request.get_json()["email"] = "amir+{}@appsembler.com".format(
            str(randint(1000, 99999))
        )
        self.request.get_data.return_value = b'{"id":820982911946154508,"email":"jon@doe.ca","closed_at":null,"created_at":"2020-03-27T13:01:19-04:00","updated_at":"2020-03-27T13:01:19-04:00","number":234,"note":null,"token":"123456abcd","gateway":null,"test":true,"total_price":"5.00","subtotal_price":"-5.00","total_weight":0,"total_tax":"0.00","taxes_included":false,"currency":"USD","financial_status":"voided","confirmed":false,"total_discounts":"5.00","total_line_items_price":"0.00","cart_token":null,"buyer_accepts_marketing":true,"name":"#9999","referring_site":null,"landing_site":null,"cancelled_at":"2020-03-27T13:01:19-04:00","cancel_reason":"customer","total_price_usd":null,"checkout_token":null,"reference":null,"user_id":null,"location_id":null,"source_identifier":null,"source_url":null,"processed_at":null,"device_id":null,"phone":null,"customer_locale":"en","app_id":null,"browser_ip":null,"landing_site_ref":null,"order_number":1234,"discount_applications":[{"type":"manual","value":"5.0","value_type":"fixed_amount","allocation_method":"one","target_selection":"explicit","target_type":"line_item","description":"Discount","title":"Discount"}],"discount_codes":[],"note_attributes":[],"payment_gateway_names":["visa","bogus"],"processing_method":"","checkout_id":null,"source_name":"web","fulfillment_status":"pending","tax_lines":[],"tags":"","contact_email":"jon@doe.ca","order_status_url":"https:\\/\\/amirtds.myshopify.com\\/28323282989\\/orders\\/123456abcd\\/authenticate?key=abcdefg","presentment_currency":"USD","total_line_items_price_set":{"shop_money":{"amount":"0.00","currency_code":"USD"},"presentment_money":{"amount":"0.00","currency_code":"USD"}},"total_discounts_set":{"shop_money":{"amount":"5.00","currency_code":"USD"},"presentment_money":{"amount":"5.00","currency_code":"USD"}},"total_shipping_price_set":{"shop_money":{"amount":"10.00","currency_code":"USD"},"presentment_money":{"amount":"10.00","currency_code":"USD"}},"subtotal_price_set":{"shop_money":{"amount":"-5.00","currency_code":"USD"},"presentment_money":{"amount":"-5.00","currency_code":"USD"}},"total_price_set":{"shop_money":{"amount":"5.00","currency_code":"USD"},"presentment_money":{"amount":"5.00","currency_code":"USD"}},"total_tax_set":{"shop_money":{"amount":"0.00","currency_code":"USD"},"presentment_money":{"amount":"0.00","currency_code":"USD"}},"line_items":[{"id":866550311766439020,"variant_id":33426620022829,"title":"Demo course","quantity":1,"sku":"course-v1:amirtadrisi+demo101+2020","variant_title":null,"vendor":null,"fulfillment_service":"manual","product_id":4814921662509,"requires_shipping":true,"taxable":true,"gift_card":false,"name":"Demo course","variant_inventory_management":null,"properties":[],"product_exists":true,"fulfillable_quantity":1,"grams":0,"price":"0.00","total_discount":"0.00","fulfillment_status":null,"price_set":{"shop_money":{"amount":"0.00","currency_code":"USD"},"presentment_money":{"amount":"0.00","currency_code":"USD"}},"total_discount_set":{"shop_money":{"amount":"0.00","currency_code":"USD"},"presentment_money":{"amount":"0.00","currency_code":"USD"}},"discount_allocations":[],"admin_graphql_api_id":"gid:\\/\\/shopify\\/LineItem\\/866550311766439020","tax_lines":[]},{"id":141249953214522974,"variant_id":33426620022829,"title":"Demo course","quantity":1,"sku":"course-v1:amirtadrisi+demo101+2020","variant_title":null,"vendor":null,"fulfillment_service":"manual","product_id":4814921662509,"requires_shipping":true,"taxable":true,"gift_card":false,"name":"Demo course","variant_inventory_management":null,"properties":[],"product_exists":true,"fulfillable_quantity":1,"grams":0,"price":"0.00","total_discount":"5.00","fulfillment_status":null,"price_set":{"shop_money":{"amount":"0.00","currency_code":"USD"},"presentment_money":{"amount":"0.00","currency_code":"USD"}},"total_discount_set":{"shop_money":{"amount":"5.00","currency_code":"USD"},"presentment_money":{"amount":"5.00","currency_code":"USD"}},"discount_allocations":[{"amount":"5.00","discount_application_index":0,"amount_set":{"shop_money":{"amount":"5.00","currency_code":"USD"},"presentment_money":{"amount":"5.00","currency_code":"USD"}}}],"admin_graphql_api_id":"gid:\\/\\/shopify\\/LineItem\\/141249953214522974","tax_lines":[]}],"fulfillments":[],"refunds":[],"total_tip_received":"0.0","admin_graphql_api_id":"gid:\\/\\/shopify\\/Order\\/820982911946154508","shipping_lines":[{"id":271878346596884015,"title":"Generic Shipping","price":"10.00","code":null,"source":"shopify","phone":null,"requested_fulfillment_service_id":null,"delivery_category":null,"carrier_identifier":null,"discounted_price":"10.00","price_set":{"shop_money":{"amount":"10.00","currency_code":"USD"},"presentment_money":{"amount":"10.00","currency_code":"USD"}},"discounted_price_set":{"shop_money":{"amount":"10.00","currency_code":"USD"},"presentment_money":{"amount":"10.00","currency_code":"USD"}},"discount_allocations":[],"tax_lines":[]}],"billing_address":{"first_name":"Bob","address1":"123 Billing Street","phone":"555-555-BILL","city":"Billtown","zip":"K2P0B0","province":"Kentucky","country":"United States","last_name":"Biller","address2":null,"company":"My Company","latitude":null,"longitude":null,"name":"Bob Biller","country_code":"US","province_code":"KY"},"shipping_address":{"first_name":"Steve","address1":"123 Shipping Street","phone":"555-555-SHIP","city":"Shippington","zip":"40003","province":"Kentucky","country":"United States","last_name":"Shipper","address2":null,"company":"Shipping Company","latitude":null,"longitude":null,"name":"Steve Shipper","country_code":"US","province_code":"KY"},"customer":{"id":115310627314723954,"email":"john@test.com","accepts_marketing":false,"created_at":null,"updated_at":null,"first_name":"John","last_name":"Smith","orders_count":0,"state":"disabled","total_spent":"0.00","last_order_id":null,"note":null,"verified_email":true,"multipass_identifier":null,"tax_exempt":false,"phone":null,"tags":"","last_order_name":null,"currency":"USD","accepts_marketing_updated_at":null,"marketing_opt_in_level":null,"admin_graphql_api_id":"gid:\\/\\/shopify\\/Customer\\/115310627314723954","default_address":{"id":715243470612851245,"customer_id":115310627314723954,"first_name":null,"last_name":null,"company":null,"address1":"123 Elm St.","address2":null,"city":"Ottawa","province":"Ontario","country":"Canada","zip":"K2H7A8","phone":"123-123-1234","name":"","province_code":"ON","country_code":"CA","country_name":"Canada","default":true}}}'
        self.request.headers = {
            "X-Shopify-Topic": "orders/paid",
            "X-Shopify-Shop-Domain": "amirtds.myshopify.com",
            "X-Shopify-Hmac-SHA256": "CRl2fOMDEZd6Inc+FjpWsvJbz7kxRlZ2yR2fyTGlyYQ=",
        }

    def test_unpaid_request(self):
        self.request.get_json()['financial_status'] = "unpaid"
        result = functions.main(self.request)
        self.assertEqual(
            result.response[0].decode(),
            "Can't handle unpaid calls"
        )

    def test_existing_user(self):
        self.request.get_json()["email"] = "amir@appsembler.com"
        result = functions.register_in_tahoe(self.request)
        self.assertEqual(
            result.response[0].decode(),
            "User {} already exist".format(self.request.get_json()["email"])
        )

    def test_registering_new_user(self):
        result = functions.register_in_tahoe(self.request)
        self.assertEqual(
            result.response[0].decode(),
            "User successfully registered in"
        )

    def test_non_existing_course(self):
        self.request.get_json()['line_items'][0]['sku'] = "invalid id"
        result = functions.enroll_in_course(self.request)
        self.assertEqual(
            result.response[0].decode(),
            "Course doesn't exist"
        )

    def test_sucessful_enrollment(self):
        result = functions.enroll_in_course(self.request)
        self.assertEqual(
            result.response[0].decode(),
            "User successfully enrolled in the course"
        )


if __name__ == "__main__":
    unittest.main()
