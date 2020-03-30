import base64
import requests
import logging
import csv
from datetime import date
from os import environ
from tempfile import NamedTemporaryFile
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
        stackdriver_client = error_reporting.Client()
        mandrill_client = mandrill.Mandrill(mandrill_password)
except Exception as e:
    logging.error(str(e))


def get_tahoe_courses():
    """
    Get a list of all courses from Tahoe Courses API from one or more sites
    and create a list of shopify products based on existing courses and their
    metadata in Tahoe
    """

    shopify_products = []
    # 1. Pull courses from Tahoe site(s)
    # 1.1 Loop over Tahoe sites
    for site in tahoe_sites:
        response_courses = requests.get(site + tahoe_courses_api, timeout=60)
        # 1.2 Make sure Tahoe courses API is up
        if response_courses.ok:
            number_pages = response_courses.json()["pagination"]["num_pages"]
        else:
            msg = "Tahoe Courses API is inaccessible"
            logging.error(msg)
            stackdriver_client.report_exception()
            raise RuntimeError(msg)
        # 1.3 Get url of courses api for next pages
        courses_api_full_url = site + tahoe_courses_api
        # 1.4 loop over all paginated reposnes
        try:
            while number_pages >= 1:
                response_courses_paginated = requests.get(courses_api_full_url)
                response_json = response_courses_paginated.json()
                # 1.5 Loop over all courses on each page
                for result in response_json["results"]:
                    # 1.6 add item to products list based on courses metadata
                    product_title = result["name"]
                    product_description = result["short_description"]
                    product_sku = result["course_id"]
                    product_image = result["media"]["image"].get("large", "")
                    product = {
                        "product_title": product_title,
                        "product_description": product_description,
                        "product_sku": product_sku,
                        "product_image": product_image,
                        "product_tag": site,
                    }
                    shopify_products.append(product)
                # 1.7 create next page url based on pagination next value
                courses_api_full_url = response_json["pagination"]["next"]
                number_pages -= 1
        except Exception as e:
            logging.error(e)
            stackdriver_client.report_exception()
    return shopify_products


def create_shopify_products(shopify_products):
    """
    Connect to shopify store, create products based on shopify_products dict
    coming from get_tahoe_courses() function and notify admins about product
    creation
    """
    try:
        # connect to shopify store
        shopify.ShopifyResource.set_site(shopify_store_admin_api)
        store = shopify.Shop.current()
        store_admin_name = store.name
        store_admin_email = store.customer_email
        # 1 Create products in store
        # 1.1 find existing SKUs from shopify to checkproduct doesn't exist
        variants = shopify.Variant.find()
        # SKU in shopify is Course ID in OpenEDX
        skus = []
        number_created_products = 0
        created_products_list = []
        for variant in variants:
            # Fill SKUs list with all courses id that exist in shopify
            skus.append(variant.sku)
        # 1.2 loop over shopify_products and create store products
        # shopify_products contains course metadata coming from OpenEDX
        for product in shopify_products:
            # 1.3 Check if the course already exist in store
            # Remember product_sku = result["course_id"]
            if not product["product_sku"] in skus:
                # 1.4 create products in store
                new_product = shopify.Product()
                new_image = shopify.Image()
                new_product.title = product["product_title"]
                new_product.body_html = product["product_description"]
                new_product.published = "false"
                new_product.published_at = ""
                # tag is site full URL
                new_product.tags = product["product_tag"]
                new_variant = shopify.Variant(
                    {
                        "sku": product["product_sku"],
                        "requires_shipping": False,
                        "inventory_policy": "deny",
                    }
                )
                new_product.variants = [new_variant]
                product_saved = new_product.save()
                if product_saved:
                    logging.info(
                        "{}: {} created successfully".format(
                            product["product_title"], product["product_sku"]
                        )
                    )
                else:
                    logging.error(
                        "unexpected error happened for {}: {} creation".format(
                            product["product_title"], product["product_sku"]
                        )
                    )
                new_image.src = product["product_image"]
                new_product.images = new_image
                new_image.product_id = new_product.id
                image_saved = new_image.save()
                if not image_saved and not product["product_image"]:
                    logging.error("{}: {} image didn't get saved")
                number_created_products += 1
                created_products_list.append(
                    [
                        product["product_title"],
                        product["product_sku"],
                        product["product_tag"],
                        date.today().strftime("%m-%d-%Y"),
                    ]
                )
            else:
                continue
        logging.info("{} product(s) created usccessfully".format(
            number_created_products
            )
        )
        # 2 Notify admins via email with created courses report
        # 2.1 Create CSV file from created products
        if number_created_products:
            text = "Number of created products in shopify: {} ".format(
                number_created_products
            )
            header = ["Product Name", "Product SKU", "Tahoe URL", "Created AT"]
            fp = NamedTemporaryFile(
                delete=False,
                prefix="created_product_",
                suffix=".csv",
                mode="w",
                dir="/tmp/",
            )
            writer = csv.writer(fp, quotechar='"', quoting=csv.QUOTE_ALL)
            writer.writerow(header)
            for created_product in created_products_list:
                writer.writerow(created_product)
            fp.flush()
            fp.close()
            data = open(fp.name, "rb").read()
            message = {
                "attachments": [
                    {
                        "content": base64.b64encode(data).decode("utf-8"),
                        "name": fp.name.split("/")[2],
                        "type": "text/csv",
                    }
                ],
                "from_email": "technical@appsembler.com",
                "from_name": "Appsembler Technical Support",
                "important": True,
                "subject": "You'r Shopify product creation report",
                "text": text,
                "to": [
                    {
                        "email": store_admin_email,
                        "name": store_admin_name,
                        "type": "to",
                    },
                    {
                        "email": "amir@appsembler.com",
                        "name": "Amir Tadrisi",
                        "type": "to",
                    },
                ],
            }
            if environment == "prod":
                mandrill_client.messages.send(message=message)
        return Response(
            "{} Product(s) got created".format(number_created_products),
            status=201
        )
    except Exception as e:
        logging.error(e)
        if environment == "prod":
            stackdriver_client.report_exception()


def main(request):
    tahoe_courses = get_tahoe_courses()
    create_shopify_products(tahoe_courses)
