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
    """
    shopify.ShopifyResource.set_site(shopify_store_admin_api)
    store = shopify.Shop.current()
    store_admin_name = store.name
    store_admin_email = store.customer_email
    request_json = request.get_json()
    product_id = request_json["line_items"][0]["product_id"]
    product = shopify.Product.find(product_id)
    # course_id = product.variants[0].sku
    course_id = request_json['line_items'][0]['sku']
    tahoe_site_url = product.tags
    email = request_json["email"]
    fullname = request_json["billing_address"]["name"]
    payment_confirmed = request_json['confirmed']
    info = {
        "course_id": course_id,
        "tahoe_site_url": tahoe_site_url,
        "customer_email": email,
        "customer_fullname": fullname,
        "payment_confirmed": payment_confirmed,
        "store_admin_name": store_admin_name,
        "store_admin_email": store_admin_email

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
     important data like Tahoe site url and user's data. First we make
     a request to tahoe_users_api and create a list of all existing users.
     If the email in request object already exists in tahoe_users_api response
     we ignore user registration if not we create a username based on
     the email and sending email, fullname and username to
     tahoe_registration_api
    """
    logging.info("Start registering user")
    logging.info(request)
    # 3.1 Get the product info from request
    info = get_info(request)
    tahoe_site_url = info.get("tahoe_site_url", "")
    # 3.2 Get a list of all users in Tahoe site
    tahoe_token = give_me_token(tahoe_site_url)
    reponse_users = requests.get(
        tahoe_site_url + tahoe_users_api,
        headers={"Authorization": "Token {}".format(tahoe_token)},
    )
    email = info.get("customer_email", "")
    fullname = info.get("customer_fullname", "")
    # 3.3 make a list of existing emails in Tahoe site
    emails = [result["email"] for result in reponse_users.json()["results"]]
    # 3.4 Make sure the user dowsn't exist
    if email in emails:
        msg = "We couldn't register {} ".format(tahoe_site_url)
        msg += "because a user with email {} already exist".format(email)
        logging.error(msg)
        if environment == "prod":
            stackdriver_client.report_exception()
        email_notifier(
            msg,
            "Tahoe User Registration",
            info["store_admin_name"],
            info["store_admin_name"]
        )
        return Response(
            "User {} already exist".format(email),
            status=409
        )
    # 3.5 Create user info in case user doesn't exist
    username = email.split("@")[0] + str(randint(1000, 9999))
    username = username.replace("+", "")
    user_info = {"name": fullname, "username": username, "email": email}
    # 3.6 Send Email, Fullname and username by POST to Registration API
    tahoe_token = give_me_token(tahoe_site_url)
    response = requests.post(
        tahoe_site_url + tahoe_registration_api,
        headers={"Authorization": "Token {}".format(tahoe_token)},
        data=user_info,
    )
    # 3.7 Process response code
    if response.ok:
        msg = "User {} successfully registered in {}".format(
            username, tahoe_site_url
        )
        logging.info(msg)
        email_notifier(msg, "Tahoe User Registration")
    elif response.status_code == 409:
        msg = "user {} already exist in {}".format(username, tahoe_site_url)
        logging.warn(msg)
        email_notifier(msg, "Tahoe User Registration")
        return False
    else:
        msg = "Something went wrong during registring {} in {}".format(
            username,
            tahoe_site_url
        )
        logging.error(msg)
        email_notifier(msg, "Tahoe User Registration")
        return False
    logging.info(response.json())
    logging.info("End of registering user")
    return Response(
        "User successfully registered in", 201
    )


# 4. Enroll the user in the course
def enroll_in_course(request):
    """
    This function is in charge of enrolling a user in a course in Tahoe site.
    first we make a request to tahoe_courses_api to get a list of all
    existing courses in specific Tahoe site, next we check if Shopify product
    SKU is valid course-id and it exist in tahoe_courses_api response
    if yes we make a call to tahoe_enrollment_api with learner's info to
    enroll him/her in that course
    """
    logging.info("Start Enrolling")
    # 4.1 Make sure the course exist
    info = get_info(request)
    email = info.get("customer_email", "")
    sku = info.get("course_id", "")
    tahoe_site_url = info.get("tahoe_site_url", "")
    response_courses = requests.get(tahoe_site_url + tahoe_courses_api)
    courses_on_site = [
        course["course_id"] for course in response_courses.json()["results"]
    ]
    if sku not in courses_on_site:
        msg = "Course {sku} doesn't exist".format(sku=sku)
        logging.error(msg)
        if environment == "prod":
            stackdriver_client.report_exception()
        email_notifier(msg, "Tahoe User Enrollment")
        return Response("Course doesn't exist", status=404)

    # 4.2 Make a call to enrollment API with email, course-id and enroll
    enrollment_info = {
        "action": "enroll",
        "email_learners": "true",
        "courses": [sku],
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
    if response.ok:
        msg = "{email} successfully enrolled into {course}".format(
            email=email, course=sku
        )
        logging.info(msg)
        email_notifier(
            msg,
            "Tahoe User Enrollment",
            info["store_admin_name"],
            info["store_admin_name"]
        )
    else:
        msg = "Error occured with enrollment of {email} to {course}".format(
            email=email, course=sku
        )
        logging.error(msg)
        email_notifier(msg, "Tahoe User Enrollment")
        return False
    logging.info(response.json())
    logging.info("End of enrollemnt")
    return Response("User successfully enrolled in the course", status=200)


# 4. Run all the defined functions
def main(request):
    if request.get_json()['financial_status'] == "paid":
        # 4.1 Run user's registration
        register_in_tahoe(request)
        # 4.2 Run user's enrollment
        enroll_in_course(request)
        return Response("200 OK", status=200)
    else:
        return Response("Can't handle unpaid calls", status=200)
