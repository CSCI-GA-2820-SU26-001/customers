######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
YourResourceModel Service

This service implements a REST API that allows you to Create, Read, Update
and Delete YourResourceModel
"""

from flask import jsonify, request, abort
from flask import current_app as app  # Import Flask application
from service.models import Customer, DataValidationError
from service.common import status  # HTTP Status Codes


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return (
        "Reminder: return some useful information in json format about the service here",
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


######################################################################
#  C R E A T E   C U S T O M E R
######################################################################
def check_content_type(content_type):
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )


@app.route("/customers", methods=["POST"])
def create_customer():
    """Create a Customer"""
    app.logger.info("Request to create a customer")

    check_content_type("application/json")

    customer = Customer()

    try:
        customer.deserialize(request.get_json())
    except DataValidationError as error:
        abort(status.HTTP_400_BAD_REQUEST, str(error))

    if Customer.find(customer.user_id):
        abort(
            status.HTTP_409_CONFLICT,
            f"Customer with user_id '{customer.user_id}' already exists.",
        )

    customer.create()

    app.logger.info("Customer with user_id %s created.", customer.user_id)

    return jsonify(customer.serialize()), status.HTTP_201_CREATED


######################################################################
#  U P D A T E   C U S T O M E R
######################################################################
@app.route("/customers/<string:user_id>", methods=["PUT"])
def update_customer(user_id):
    """
    Update an existing Customer
    """
    app.logger.info("Request to update customer with user_id: %s", user_id)

    check_content_type("application/json")

    customer = Customer.find(user_id)

    if not customer:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Customer with user_id '{user_id}' was not found.",
        )

    try:
        data = request.get_json()
        data["user_id"] = user_id  # URL is source of truth
        customer.deserialize(data)
    except DataValidationError as error:
        abort(status.HTTP_400_BAD_REQUEST, str(error))

    customer.update()

    app.logger.info("Customer with user_id %s updated.", user_id)

    return jsonify(customer.serialize()), status.HTTP_200_OK
#  D E L E T E   C U S T O M E R
######################################################################
@app.route("/customers/<string:user_id>", methods=["DELETE"])
def delete_customer(user_id):
    """
    Delete a Customer

    This endpoint will delete a Customer based on the user_id provided.
    Returns 204 No Content whether or not the customer existed (idempotent).
    """
    app.logger.info("Request to delete customer with user_id: %s", user_id)

    customer = Customer.find(user_id)
    if customer:
        customer.delete()
        app.logger.info("Customer with user_id %s deleted.", user_id)
    else:
        app.logger.info(
            "Customer with user_id %s not found — no action taken (idempotent).",
            user_id,
        )

    return "", status.HTTP_204_NO_CONTENT
