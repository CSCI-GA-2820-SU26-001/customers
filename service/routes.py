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
from flask_restx import Api, Resource, Namespace
from werkzeug.exceptions import (
    BadRequest,
    NotFound,
    Conflict,
    UnsupportedMediaType,
    MethodNotAllowed,
)
from service.models import Customer, DataValidationError
from service.common import status  # HTTP Status Codes


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    app.logger.info("Request to root URL /")

    response = {
        "name": "Customers Service",
        "message": "Welcome to the Customers service API",
        "status": "running",
        "links": {"customers": "/customers"},
    }

    return jsonify(response), status.HTTP_200_OK
    # return (
    #     "Reminder: return some useful information in json format about the service here",
    #     status.HTTP_200_OK,
    # )


######################################################################
# HEALTH CHECK
######################################################################
@app.route("/health")
def health():
    """Health endpoint for Kubernetes liveness/readiness probes"""
    return jsonify(status="OK"), status.HTTP_200_OK


######################################################################
# Configure Flask-RESTX
######################################################################
api = Api(
    app,
    version="1.0.0",
    title="Customer REST API Service",
    description="This is the Customer service that manages customer accounts.",
    default="customers",
    default_label="Customer operations",
    doc="/apidocs",
    prefix="/api",
)

# pylint: disable=invalid-name
ns = Namespace("customers", description="Customer operations")
api.add_namespace(ns, path="/customers")


######################################################################
#  U T I L I T Y   F U N C T I O N S
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


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


######################################################################
#  PATH: /api/customers
######################################################################
@ns.route("", strict_slashes=False)
class CustomerCollection(Resource):
    """
    CustomerCollection

    Allows interaction with the collection of Customers:
    GET /api/customers  - List all Customers
    POST /api/customers - Create a Customer
    """

    # ------------------------------------------------------------------
    # LIST ALL CUSTOMERS
    # ------------------------------------------------------------------
    def get(self):
        """
        List all Customers

        This endpoint returns all Customers in the database.
        An empty list is returned if no customers exist.
        """
        app.logger.info("Request to list all customers")

        customers = Customer.all()

        results = [customer.serialize() for customer in customers]

        app.logger.info("Returning %d customers", len(results))

        return results, status.HTTP_200_OK

    # ------------------------------------------------------------------
    # CREATE A NEW CUSTOMER
    # ------------------------------------------------------------------
    def post(self):
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

        location_url = api.url_for(CustomerResource, user_id=customer.user_id)

        return customer.serialize(), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
#  PATH: /api/customers/<user_id>
######################################################################
@ns.route("/<string:user_id>")
@ns.param("user_id", "The Customer identifier")
class CustomerResource(Resource):
    """
    CustomerResource

    Allows interaction with a single Customer:
    GET /api/customers/{user_id} - Read a Customer
    PUT /api/customers/{user_id} - Update a Customer
    DELETE /api/customers/{user_id} - Delete a Customer
    """

    # ------------------------------------------------------------------
    # READ A CUSTOMER
    # ------------------------------------------------------------------
    def get(self, user_id):
        """
        Read a Customer

        This endpoint will return a Customer based on the user_id provided.
        """
        app.logger.info("Request to read customer with user_id: %s", user_id)

        customer = Customer.find(user_id)

        if not customer:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Customer with user_id '{user_id}' was not found.",
            )

        app.logger.info("Returning customer with user_id: %s", user_id)

        return customer.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # UPDATE AN EXISTING CUSTOMER
    # ------------------------------------------------------------------
    def put(self, user_id):
        """Update an existing Customer"""
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
            data["user_id"] = user_id
            customer.deserialize(data)
        except DataValidationError as error:
            abort(status.HTTP_400_BAD_REQUEST, str(error))

        customer.update()

        app.logger.info("Customer with user_id %s updated.", user_id)

        return customer.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE A CUSTOMER
    # ------------------------------------------------------------------
    def delete(self, user_id):
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


######################################################################
#  Q U E R Y   +   S U S P E N D   (not yet migrated — see issue #53)
######################################################################
# Per issue #52's assumptions, Query and Suspend stay on their
# pre-migration, plain-Flask routes and outside the /api prefix until
# the follow-up "Migrate Query and Suspend Action routes to
# Flask-RESTX" story. Keeping them here (rather than deleting them)
# means #52 stays scoped to CRUD + List while #52's own acceptance
# criteria ("each behaves identically to the pre-migration routes")
# still holds for the parts of the surface this story didn't touch.
@app.route("/customers", methods=["GET"])
def query_customers():
    """
    Query Customers by first_name and/or last_name

    NOTE: this is the pre-migration List/Query endpoint. The migrated
    List endpoint (GET /api/customers, above) does not filter — that
    capability lives here until #53 moves it under /api.
    """
    app.logger.info("Request to list customers")

    first_name = request.args.get("first_name")
    last_name = request.args.get("last_name")

    if first_name and last_name:
        app.logger.info(
            "Filtering customers by first_name=%s and last_name=%s",
            first_name,
            last_name,
        )
        customers = Customer.find_by_name(first_name, last_name)
    elif first_name:
        app.logger.info("Filtering customers by first_name=%s", first_name)
        customers = Customer.find_by_first_name(first_name)
    elif last_name:
        app.logger.info("Filtering customers by last_name=%s", last_name)
        customers = Customer.find_by_last_name(last_name)
    else:
        customers = Customer.all()

    results = [customer.serialize() for customer in customers]

    app.logger.info("Returning %d customers", len(results))

    return jsonify(results), status.HTTP_200_OK


@app.route("/customers/<string:user_id>/suspend", methods=["PUT"])
def suspend_customer(user_id):
    """Suspend a Customer account"""
    app.logger.info("Request to suspend customer with user_id: %s", user_id)

    customer = Customer.find(user_id)

    if not customer:
        # flask.abort() here wouldn't get JSON-formatted by our
        # @api.errorhandler(NotFound) handlers below — those only fire
        # for requests Flask-RESTX owns (paths under /api), and this
        # route is deliberately outside /api. Build the JSON body
        # directly instead of relying on error-handler wiring meant
        # for a different URL prefix.
        message = f"Customer with user_id '{user_id}' was not found."
        app.logger.warning(message)
        return (
            jsonify(
                status=status.HTTP_404_NOT_FOUND, error="Not Found", message=message
            ),
            status.HTTP_404_NOT_FOUND,
        )

    customer.suspended = True
    customer.update()

    app.logger.info("Customer with user_id %s suspended.", customer.user_id)

    return jsonify(customer.serialize()), status.HTTP_200_OK


######################################################################
#  E R R O R   H A N D L E R S
######################################################################
# Flask-RESTX intercepts exceptions raised inside its own Resource
# classes before Flask's app-level @app.errorhandler functions in
# service/common/error_handlers.py ever see them. These handlers keep
# the JSON error contract ({"status", "error", "message"}) identical
# to the pre-migration routes so no client-visible behavior changes.
def _error_body(code, error, message):
    return {"status": code, "error": error, "message": message}, code


@api.errorhandler(DataValidationError)
def handle_data_validation_error(error):
    """Handles Value Errors from bad data"""
    message = str(error)
    app.logger.warning(message)
    return _error_body(status.HTTP_400_BAD_REQUEST, "Bad Request", message)


@api.errorhandler(BadRequest)
def handle_bad_request(error):
    """Handles 400 Bad Request"""
    message = str(error)
    app.logger.warning(message)
    return _error_body(status.HTTP_400_BAD_REQUEST, "Bad Request", message)


@api.errorhandler(NotFound)
def handle_not_found(error):
    """Handles 404 Not Found"""
    message = str(error)
    app.logger.warning(message)
    return _error_body(status.HTTP_404_NOT_FOUND, "Not Found", message)


@api.errorhandler(Conflict)
def handle_conflict(error):
    """Handles 409 Conflict"""
    message = str(error)
    app.logger.warning(message)
    return _error_body(status.HTTP_409_CONFLICT, "Conflict", message)


@api.errorhandler(UnsupportedMediaType)
def handle_unsupported_media_type(error):
    """Handles 415 Unsupported Media Type"""
    message = str(error)
    app.logger.error(message)
    return _error_body(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "Unsupported media type", message
    )


@api.errorhandler(MethodNotAllowed)
def handle_method_not_allowed(error):
    """Handles 405 Method Not Allowed"""
    message = str(error)
    app.logger.warning(message)
    return _error_body(
        status.HTTP_405_METHOD_NOT_ALLOWED, "Method not Allowed", message
    )


@api.errorhandler
def handle_internal_server_error(error):
    """Handles any other unexpected server error with 500"""
    message = str(error)
    app.logger.error(message)
    return _error_body(
        status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal Server Error", message
    )
