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


shopify_secret = environ.get("shopify_secret", "")
shopify_store_url = environ.get("shopify_store_url", "")
environment = environ.get("env", "")
purchase_listerner_url = environ.get('purchase_listerner_url', '')
product_validator_url = environ.get('product_validator_url', '')

shopify_topics_handler = {
    "orders/paid": purchase_listerner_url,
    "products/create": product_validator_url,
    "products/update": product_validator_url,
}

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
    This function receives a call from Shopify when an end-user makes
    a paid transaction in the store or Shopify admin creates or updates
    a product in the store. Steps to validate the call are
    1- Making sure the signature is valid
    2- Check if the call is coming from the store and not from
    unauthorized caller
    3- If the call made during product purchase, Make sure the request
    contains necessary data for us to register and enroll the user in Tahoe
    After validation is done and the call is valid, we trigger proper
    Cloud functions with the request object. if the original call happened
    after successful purchase we trigger successful_purchase_listener and if
    the original call happened because fo product creation or update in Shopify
    we trigger shopify_product_validator. shopify_call_validator execution
    ends by sending a 200 response to Shopify. The reason is Shopify waits
    for 5 seconds to receive a 200 ack from us and if they don't receive it,
    they keep making a call to the function because they assume
    we didn't receive the call.
    """
    try:
        logging.info("Start validating a call")
        # 1.1 Verify store signature
        request_json = request.get_json()
        # logged request only contains non critical data
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
            if request_json["financial_status"] == "paid":
                # 1.3 Verify Shopify's call contains email, fullname and SKU
                # Only purchase call contains this data
                email = request_json["email"]
                fullname = request_json["billing_address"]["name"]
                line_items = request_json["line_items"]
                skus = [line_item["sku"] for line_item in line_items]
                if not email or not fullname or not skus:
                    msg = "Bad request - Email or fullname or sku missing"
                    logging.info(request_json)
                    logging.error(msg)
                    return Response(
                        "Email or fullname or sku missing",
                        status=200
                    )
                else:
                    msg = "purchase call from {} - {} for {} is valid".format(
                        caller, email, skus
                    )
                    logging.info(msg)
                    function_url = shopify_topics_handler["orders/paid"]
                    pool = Pool(1)
                    pool.apply_async(
                        requests.post,
                        args=[function_url],
                        kwds={"json": request_json}
                    )
                    logging.info("sent a request to {}".format(function_url))
                    logging.info("End of call validation")
                    return Response(
                        "Call is valid redirected to {}".format(function_url),
                        status=200,
                    )
            else:
                return Response("Cant handle unpaid call", status=200)
        elif topic == "products/create" or topic == "products/update":
            function_url = shopify_topics_handler["products/create"]
            pool = Pool(1)
            # 1.3 Async call to other function
            pool.apply_async(
                requests.post, args=[function_url], kwds={"json": request_json}
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
