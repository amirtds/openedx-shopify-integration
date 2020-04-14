import logging
from random import randint
from os import environ
from flask import Response

import requests
import shopify
from google.cloud import error_reporting
import mandrill

shopify_secret = environ.get("shopify_secret", "")
shopify_store_url = environ.get("shopify_store_url", "")
shopify_store_admin_api = environ.get("shopify_store_admin_api", "")
tahoe_sites = environ.get("tahoe_sites", "").split(",")
tahoe_courses_api = environ.get("tahoe_courses_api", "")
tahoe_registration_api = environ.get("tahoe_registration_api", "")
tahoe_enrollment_api = environ.get("tahoe_enrollment_api", "")
tahoe_users_api = environ.get("tahoe_users_api", "")
tahoe_sites_tokens = environ.get("tahoe_sites_tokens", "")
mandrill_password = environ.get("mandrill_password", "")
environment = environ.get("env", "")

try:
    if environment == "prod":
        mandrill_client = mandrill.Mandrill(mandrill_password)
        stackdriver_client = error_reporting.Client()
except Exception as e:
    logging.error(str(e))


def give_me_token(tahoe_site_url):
    sites_tokens_dict = {}
    sites_tokens_list = tahoe_sites_tokens.split(",")
    for item in sites_tokens_list:
        sites_tokens_dict[item.split(";")[0]] = item.split(";")[1]
    return sites_tokens_dict.get(tahoe_site_url, "")


# 1 Get Shopify Product and Customer information
def get_info(request):
    """
        Get product and customer information from shopify webhook request
        tahoe_site_urls dict contains course id and tahoe url where that
        course is hosted
     {
       'course-v1:amirtadrisi+tree1+2020_1': 'https://amirtadrisi.tahoe.com',
       'course-v1:amirtadrisi+demo101+2020': 'https://other-site.tahoe.com'}
    }
    """
    shopify.ShopifyResource.set_site(shopify_store_admin_api)
    store = shopify.Shop.current()
    request_json = request.get_json()
    line_items = request_json['line_items']
    store_admin_name = store.name
    store_admin_email = store.customer_email
    product_ids = [line_item["product_id"] for line_item in line_items]
    tahoe_site_urls = {}
    for product_id in product_ids:
        product = shopify.Product.find(product_id)
        tahoe_site_urls[product.variants[0].sku] = product.tags
    course_ids = [line_item['sku'] for line_item in line_items]
    email = request_json["email"]
    fullname = request_json["billing_address"]["name"]
    first_name = request_json["billing_address"]["first_name"]
    username = first_name + str(randint(100, 9999))
    payment_confirmed = request_json['confirmed']
    info = {
        "course_id": course_ids,
        "tahoe_site_urls": tahoe_site_urls,
        "customer_email": email,
        "customer_fullname": fullname,
        "payment_confirmed": payment_confirmed,
        "store_admin_name": store_admin_name,
        "store_admin_email": store_admin_email,
        "username": username

    }
    return info


# 2. Email notifier function
def email_notifier(msg, subject, store_admin_email="", store_admin_name=""):
    message = {
        "from_email": "technical@appsembler.com",
        "from_name": "Appsembler Technical Support",
        "important": True,
        "subject": subject,
        "text": msg,
        "to": [
            {"email": "amir@appsembler.com", "name": "Amir Tadrisi", "type": "to",},
        ],
    }
    if store_admin_email:
        message["to"].append(
            {"email": store_admin_email, "name": store_admin_name, "type": "to",},
        )
    if environment == "prod":
        mandrill_client.messages.send(message=message)


# 3. Register the user in Tahoe
def register_in_tahoe(request):
    """
     This function registers a user in Tahoe site in case the user is not
     already registered. To do that we get the necessary info from the request
     object coming from shopify_call_validator, this request contains
     important data like Tahoe site url and user's data.
     Then we create a username based on the email and sending email,
     fullname and username to tahoe_registration_api.
    """
    logging.info("Start registering user")
    logging.info(request.get_json())
    # 3.1 Get the product info from request
    info = get_info(request)
    tahoe_site_urls = info.get("tahoe_site_urls", "")
    email = info.get("customer_email", "")
    fullname = info.get("customer_fullname", "")
    # 3.2 Create user info
    username = info.get('username', '')
    username = username.replace("+", "")
    user_info = {"name": fullname, "username": username, "email": email}
    # 3.3 Send Email, Fullname and username by POST to Registration API
    for _, tahoe_site_url in tahoe_site_urls.items():
        tahoe_token = give_me_token(tahoe_site_url)
        response = requests.post(
            tahoe_site_url + tahoe_registration_api,
            headers={"Authorization": "Token {}".format(tahoe_token)},
            data=user_info,
        )
        # 3.4 Process response code
        if response.ok:
            msg = "User {} successfully registered in {}".format(
                username, tahoe_site_url
            )
            logging.info(msg)
            if environment == "prod":
                email_notifier(msg, "Tahoe User Registration")
        elif response.status_code == 409:
            msg = "user {} already exist in {}".format(
                username, tahoe_site_url
            )
            logging.warn(msg)
            if environment == "prod":
                email_notifier(msg, "Tahoe User Registration")
        else:
            msg = "Something went wrong during registring {} in {}".format(
                username,
                tahoe_site_url
            )
            logging.error(msg)
            if environment == "prod":
                email_notifier(msg, "Tahoe User Registration")
        logging.info(response.json())
    logging.info("End of registering user")
    return Response(
        "End of registering user",
        status=207
    )


# 4. Enroll the user in the course
def enroll_in_course(request):
    """
    This function is in charge of enrolling a user in a course(s) in
    Tahoe site(s). We make a call to tahoe_enrollment_api with
    learner's info to enroll him/her in the course(s)
    """
    logging.info("Start Enrolling")
    # 4.1 Get important info from the request
    info = get_info(request)
    email = info.get("customer_email", "")
    tahoe_site_urls = info.get("tahoe_site_urls", "")
    # 4.2 Make a call to enrollment API with email, course-id and enroll
    # 4.2 We need to loop over all courses coming from the purchase
    for course_id, tahoe_site_url in tahoe_site_urls.items():
        enrollment_info = {
            "action": "enroll",
            "email_learners": "false",
            "courses": course_id,
            "identifiers": [email],
            "auto_enroll": "true",
        }
        tahoe_token = give_me_token(tahoe_site_url)
        response = requests.post(
            tahoe_site_url + tahoe_enrollment_api,
            headers={"Authorization": "Token {}".format(tahoe_token)},
            data=enrollment_info,
        )
        # 4.3 Process response code from Tahoe
        logging.info(response.json())
        if response.ok:
            msg = "{email} successfully enrolled into {course}".format(
                email=email, course=course_id
            )
            logging.info(msg)
            if environment == "prod":
                email_notifier(
                    msg,
                    "Tahoe User Enrollment",
                    info["store_admin_name"],
                    info["store_admin_name"]
                )
        elif response.status_code == 400:
            msg = "Error occured while enrolling {email} to {course} ".format(
                email=email, course=course_id
            )
            msg += "{} is not a valid course in {}".format(
                course_id,
                tahoe_site_url
            )
            logging.error(msg)
            if environment == "prod":
                email_notifier(msg, "Tahoe User Enrollment")
        else:
            msg = "Error occured while enrolling {email} to {course}".format(
                email=email, course=course_id
            )
            logging.error(msg)
            if environment == "prod":
                email_notifier(msg, "Tahoe User Enrollment")
    logging.info("End of enrollemnt")
    return Response("End of enrollemnt", status=207)


# 4. Run all the registration and enrollment
def main(request):
    if request.get_json()['financial_status'] == "paid":
        # 4.1 Run user's registration
        register_in_tahoe(request)
        # 4.2 Run user's enrollment
        enroll_in_course(request)
        # 4.3 send ack to shopify
        return Response("200 OK", status=200)
    else:
        return Response("Can't handle unpaid calls", status=200)
