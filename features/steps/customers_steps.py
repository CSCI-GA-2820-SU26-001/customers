# # pylint: disable=no-name-in-module, not-callable


# """
# Customer Step Definitions
# """

# import requests
# from behave import given
# from compare3 import expect

# # HTTP Status Codes
# HTTP_200_OK = 200
# HTTP_201_CREATED = 201
# HTTP_204_NO_CONTENT = 204

# WAIT_TIMEOUT = 60


# ######################################################################
# # Given the following customers
# ######################################################################
# @given("the following customers")
# def step_impl(context):
#     """Delete all existing customers and create the ones in the table"""

#     # Remove any existing customers

#     customers_url = f"{context.base_url}/api/customers"

#     response = requests.get(customers_url, timeout=WAIT_TIMEOUT)

#     expect(response.status_code).equal_to(HTTP_200_OK)

#     for customer in response.json():

#         requests.delete(f"{customers_url}/{customer['user_id']}", timeout=WAIT_TIMEOUT)

#     # Create the customers from the feature table

#     for row in context.table:

#         customer = {
#             "user_id": row["user_id"],
#             "first_name": row["first_name"],
#             "last_name": row["last_name"],
#             "address": row["address"],
#         }

#         response = requests.post(customers_url, json=customer, timeout=WAIT_TIMEOUT)

#         expect(response.status_code).equal_to(HTTP_201_CREATED)
