import hmac
import hashlib
import base64
import logging
from hmac import digest
from os import environ, stat
from flask import Response
from multiprocessing.dummy import Pool


import requests
from google.cloud import error_reporting


shopify_topics_handler = {
    "orders/paid": "https://us-central1-appsembler-tahoe-0.cloudfunctions.net/test_successful_purchase_listener",
    "products/create": "https://us-central1-appsembler-tahoe-0.cloudfunctions.net/test_shopify_product_validator",
    "products/update": "https://us-central1-appsembler-tahoe-0.cloudfunctions.net/test_shopify_product_validator"
}
shopify_secret = environ.get("shopify_secret", "")
shopify_store_url = environ.get("shopify_store_url", "")
environment = environ.get("env", "")

if environment == "prod":
    try:
        stackdriver_client = error_reporting.Client()
    except Exception as e:
        logging.error(str(e))


# 1. Verify recieved data from Shopify is valid
def verify_webhook(data, hmac_header):
    secret_utf8 = shopify_secret.encode("utf-8")
    digest = hmac.new(secret_utf8, data, hashlib.sha256).digest()
    computed_hmac = base64.b64encode(digest)
    return hmac.compare_digest(computed_hmac, hmac_header.encode("utf-8"))


def call_validator(request):
    """
    This function recieves a call from shopify when user makes a paid
    transaction in the store or shopify admin creates or updates a product in
    store. First step is to validate a call by
    1- making sure the signature is valid
    2- call is coming from the store and not from unauthorized caller
    3- if the call made by product purchase we need to make sure the request
    contains necessary data for us to register and enroll the user in Tahoe
    After validation is done we send the request object to internal google
    functions to take action.
    In this function we need to return 200 in any case, because shopify waits
    for 5 seconds to recieve a 200 ack from us and if they don't recieve it
    they keep making a call to the function because they assume we didn't
    recieve the call
    """
    try:
        logging.info("Start validating a call")
        # 1.1 Verify store signature
        request_json = request.get_json()
        # request only contains non critical data
        logging.info(request_json)
        data = request.get_data()
        topic = request.headers.get("X-Shopify-Topic", "")
        caller = request.headers.get("X-Shopify-Shop-Domain", "")
        caller = "https://" + caller
        hmac_sha = request.headers.get("X-Shopify-Hmac-SHA256", "")
        varified_signature = verify_webhook(data, hmac_sha)
        if not varified_signature:
            msg = "Unauthorized access - Store signature is not valid"
            logging.info(request_json)
            logging.error(msg)
            return Response("Store signature is not valid", status=200)

        # 1.2 Verify caller is Shopify not a third party
        if caller != shopify_store_url:
            msg = "Unauthorized access - Unauthorized caller"
            logging.info(request_json)
            logging.error(msg)
            return Response("Unauthorized caller", status=200)

        if topic == "orders/paid":
            if request_json['financial_status'] == "paid":
                # 1.3 Verify that Shopify's call contains email, fullname and SKU
                # Only purchase call contains this data
                email = request_json["email"]
                fullname = request_json["billing_address"]["name"]
                sku = request_json["line_items"][0]["sku"]
                if not email or not fullname or not sku:
                    msg = "Bad request - Email or fullname or sku missing"
                    logging.info(request_json)
                    logging.error(msg)
                    return Response("Email or fullname or sku missing", status=200)
                else:
                    msg = "call from {} - {} for purchasing {} is valid".format(
                        caller, email, sku
                    )
                    logging.info(msg)
                    function_url = shopify_topics_handler["orders/paid"]
                    pool = Pool(1)
                    pool.apply_async(
                        requests.post,
                        args=[function_url],
                        kwds={'json': request_json}
                    )
                    logging.info("sent a request to {}".format(function_url))
                    logging.info("End of call validation")
                    return Response(
                        "Call is valid redirected to {}".format(function_url),
                        status=200
                        )
            else:
                return Response("Cant handle unpaid call", status=200)
        elif topic == "products/create" or topic == "products/update":
            function_url = shopify_topics_handler["products/create"]
            pool = Pool(1)
            pool.apply_async(
                requests.post,
                args=[function_url],
                kwds={'json': request_json}
            )
            logging.info("sent a request to {}".format(function_url))
            logging.info("End of call validation")
            return Response(
                "Call is valid redirected to {}".format(function_url),
                status=200
            )
        else:
            return Response("Invalid topic to handle", status=200)
    except Exception as e:
        logging.error(str(e))
        if environment == "prod":
            stackdriver_client.report_exception()
