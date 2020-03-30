import requests
import logging
from os import environ
from flask import Response

import shopify
import requests
from google.cloud import error_reporting
import mandrill

shopify_secret = environ.get("shopify_secret", "")
shopify_store_url = environ.get("shopify_store_url", "")
shopify_store_admin_api = environ.get("shopify_store_admin_api", "")
tahoe_sites = environ.get("tahoe_sites", "").split(",")
tahoe_courses_api = environ.get("tahoe_courses_api", "")
mandrill_password = environ.get("mandrill_password", "")
environment = environ.get("env", "")

try:
    if environment == "prod":
        mandrill_client = mandrill.Mandrill(mandrill_password)
        stackdriver_client = error_reporting.Client()
except Exception as e:
    logging.error(str(e))


# 1. Email notifier function
def email_notifier(msg, subject, store_admin_email="", store_admin_name=""):
    message = {
        "from_email": "technical@appsembler.com",
        "from_name": "Appsembler Technical Support",
        "important": True,
        "subject": subject,
        "text": msg,
        "to": [
            {
                "email": "amir@appsembler.com",
                "name": "Amir Tadrisi",
                "type": "to"
            }
        ]
    }
    if store_admin_email:
        message["to"].append(
            {"email": store_admin_email, "name": store_admin_name, "type": "to"}
        )
    mandrill_client.messages.send(message=message)


def shopify_product_validator(request):
    """
        This Function unpublishes a created/updated product in shopify if
        the product SKU is not valid course id or if the course doesn't exist.
        It recieves a call from shopify webhook, Loops over all specified
        Tahoe Sites, Gets a list of courses ids and checks if the SKU of 
        created/Updated Product(it is in request object) is in the list of all
        courses ids if not that product gets unpublished in shopify.
    """
    # 1 Get a list of all existing course ids in specified Tahoe sites
    # 1.1 Loop over all specified Tahoe sites
    try:
        courses_ids = []
        shopify.ShopifyResource.set_site(shopify_store_admin_api)
        store = shopify.Shop.current()
        store_admin_name = store.name
        store_admin_email = store.customer_email
        for site in tahoe_sites:
            response_courses = requests.get(site + tahoe_courses_api, timeout=120)
            if response_courses.ok:
                number_pages = response_courses.json()["pagination"]["num_pages"]
            else:
                msg = "Tahoe Courses API is inaccessible"
                logging.error(msg)
                if environment == "prod":
                    stackdriver_client.report_exception()
                raise RuntimeError(msg)
            courses_api_full_url = site + tahoe_courses_api
            while number_pages >= 1:
                response_courses_paginated = requests.get(courses_api_full_url)
                response_json = response_courses_paginated.json()
                # 1.2 Loop over all courses on each page
                for result in response_json["results"]:
                    # 1.3 add item to courses id
                    courses_ids.append(result["course_id"])
                # 1.4 create next page url based on pagination next value
                courses_api_full_url = response_json["pagination"]["next"]
                number_pages -= 1
        # 2 Make sure Shopify SKU is a valid course id
        # 2.1 reterieve sku from request object from shopify webhook request
        request_json = request.get_json()
        sku = request_json["variants"][0]["sku"]
        if sku not in courses_ids:
            logging.error("Course {sku} doesn't exist".format(sku=sku))
            # 2.2 unpublish the product in Shopify
            # 2.2.1 Find the product in our store
            product_id = request_json["id"]
            if environment == "prod":
                invalid_product = shopify.Product.find(product_id)
                title = invalid_product.title
                invalid_product.published = "false"
                invalid_product.published_at = ""
                invalid_variant = invalid_product.variants[0]
                del invalid_variant.attributes["inventory_quantity"]
                del invalid_variant.attributes["old_inventory_quantity"]
                invalid_product.save()
                # 2.3 Notify admin by Email
                msg = "You tried to update or create the '{}' in Shopify".format(
                    title
                )
                msg += " but it's SKU {} is not a valid Course ID".format(sku)
                msg += " We unpublished your product in your store."
                msg += " Please review it at {} and try again".format(
                    shopify_store_url
                )
                email_notifier(
                    msg,
                    store_admin_email,
                    store_admin_name,
                    "Invalid Course ID - Shopify call validator"
                )
            return Response("SKU wasn't valid", status=409)
        return Response("SKU is valid", status=200)
    except Exception as e:
        logging.error(str(e))
        if environment == "prod":
            stackdriver_client.report_exception()


# 3. Run main function
def main(request):
    shopify_product_validator(request)
