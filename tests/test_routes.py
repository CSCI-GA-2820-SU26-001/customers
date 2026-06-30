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
Customer API Service Test Suite
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from unittest.mock import patch
from wsgi import app
from service import create_app
from service.common import status
from service.models import db, Customer
from .factories import CustomerFactory

BASE_URL = "/customers"


DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestCustomerService(TestCase):
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Customer).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    ######################################################################
    #  C R E A T E   C U S T O M E R   T E S T S
    ######################################################################

    def test_create_customer(self):
        """It should Create a new Customer"""
        customer = CustomerFactory()
        response = self.client.post(BASE_URL, json=customer.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("Location", response.headers)
        self.assertTrue(
            response.headers["Location"].endswith(f"{BASE_URL}/{customer.user_id}")
        )
        data = response.get_json()
        self.assertEqual(data["user_id"], customer.user_id)
        self.assertEqual(data["first_name"], customer.first_name)
        self.assertEqual(data["last_name"], customer.last_name)
        self.assertEqual(data["address"], customer.address)

        new_customer = Customer.find(customer.user_id)
        self.assertIsNotNone(new_customer)
        self.assertEqual(new_customer.user_id, customer.user_id)

    def test_create_customer_missing_field(self):
        """It should not Create a Customer with missing required data"""
        customer = CustomerFactory()
        data = customer.serialize()
        data.pop("first_name")

        response = self.client.post(BASE_URL, json=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_customer_bad_content_type(self):
        """It should not Create a Customer with bad content type"""
        customer = CustomerFactory()

        response = self.client.post(
            BASE_URL,
            data=str(customer.serialize()),
            content_type="text/plain",
        )

        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_duplicate_customer(self):
        """It should not Create a Customer with duplicate user_id"""

        customer = CustomerFactory()
        customer.create()

        response = self.client.post(BASE_URL, json=customer.serialize())

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertTrue(response.is_json)

        data = response.get_json()
        self.assertEqual(data["status"], status.HTTP_409_CONFLICT)
        self.assertEqual(data["error"], "Conflict")

    ######################################################################
    #  U P D A T E   C U S T O M E R   T E S T S
    ######################################################################

    def test_update_customer(self):
        """It should Update an existing Customer"""

        customer = CustomerFactory()
        customer.create()

        update_data = customer.serialize()
        update_data["first_name"] = "Updated"
        update_data["last_name"] = "Customer"
        update_data["address"] = "456 Updated Street"

        response = self.client.put(f"{BASE_URL}/{customer.user_id}", json=update_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.get_json()

        self.assertEqual(data["user_id"], customer.user_id)
        self.assertEqual(data["first_name"], "Updated")
        self.assertEqual(data["last_name"], "Customer")
        self.assertEqual(data["address"], "456 Updated Street")

        updated = Customer.find(customer.user_id)

        self.assertEqual(updated.first_name, "Updated")
        self.assertEqual(updated.last_name, "Customer")
        self.assertEqual(updated.address, "456 Updated Street")

    def test_update_customer_not_found(self):
        """It should return 404 when updating a non-existent Customer"""

        customer = CustomerFactory()

        response = self.client.put(
            f"{BASE_URL}/does-not-exist", json=customer.serialize()
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_customer_missing_field(self):
        """It should not Update a Customer with missing required data"""

        customer = CustomerFactory()
        customer.create()

        data = customer.serialize()
        data.pop("first_name")

        response = self.client.put(f"{BASE_URL}/{customer.user_id}", json=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_customer_bad_content_type(self):
        """It should not Update a Customer with bad content type"""

        customer = CustomerFactory()
        customer.create()

        response = self.client.put(
            f"{BASE_URL}/{customer.user_id}",
            data="bad data",
            content_type="text/plain",
        )

        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_update_customer_user_id_from_url(self):
        """It should ignore user_id in body and use URL user_id"""

        customer = CustomerFactory()
        customer.create()

        data = customer.serialize()
        data["user_id"] = "different-user-id"
        data["first_name"] = "Changed"

        response = self.client.put(f"{BASE_URL}/{customer.user_id}", json=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        updated = Customer.find(customer.user_id)

        self.assertIsNotNone(updated)
        self.assertEqual(updated.first_name, "Changed")

        self.assertIsNone(Customer.find("different-user-id"))

    ######################################################################
    #  D E L E T E   C U S T O M E R   T E S T S
    ######################################################################

    def test_delete_customer(self):
        """It should Delete an existing Customer and return 204 No Content"""
        # Arrange — create a customer so there is something to delete
        customer = CustomerFactory()
        customer.create()

        # Act — send DELETE request
        response = self.client.delete(f"{BASE_URL}/{customer.user_id}")

        # Assert — 204 No Content, empty body
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)

        # Confirm the customer is actually gone from the database
        deleted = Customer.find(customer.user_id)
        self.assertIsNone(deleted)

    def test_delete_customer_not_found_is_idempotent(self):
        """It should return 204 No Content even when the Customer does not exist (idempotent DELETE)"""
        # Arrange — use an ID that was never persisted
        nonexistent_id = "user-does-not-exist-99999"

        # Act
        response = self.client.delete(f"{BASE_URL}/{nonexistent_id}")

        # Assert — idempotent: 204 regardless of prior state
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)

    def test_delete_customer_twice_is_idempotent(self):
        """It should return 204 on a second DELETE of the same Customer (idempotent)"""
        # Arrange
        customer = CustomerFactory()
        customer.create()

        # First delete
        first_response = self.client.delete(f"{BASE_URL}/{customer.user_id}")
        self.assertEqual(first_response.status_code, status.HTTP_204_NO_CONTENT)

        # Second delete of same ID — should still be 204, not an error
        second_response = self.client.delete(f"{BASE_URL}/{customer.user_id}")
        self.assertEqual(second_response.status_code, status.HTTP_204_NO_CONTENT)

        # Customer must still be gone
        self.assertIsNone(Customer.find(customer.user_id))

    ######################################################################
    #  R E A D   C U S T O M E R   T E S T S
    ######################################################################

    def test_read_customer(self):
        """It should Read an existing Customer"""
        customer = CustomerFactory()
        customer.create()

        response = self.client.get(f"{BASE_URL}/{customer.user_id}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.get_json()
        self.assertEqual(data["user_id"], customer.user_id)
        self.assertEqual(data["first_name"], customer.first_name)
        self.assertEqual(data["last_name"], customer.last_name)
        self.assertEqual(data["address"], customer.address)

    def test_read_customer_not_found(self):
        """It should return 404 when reading a non-existing Customer"""
        response = self.client.get(f"{BASE_URL}/does-not-exist")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_customer_no_content_type(self):
        """It should return 415 when Content-Type is missing"""
        customer = CustomerFactory()

        response = self.client.post(
            BASE_URL,
            data=str(customer.serialize()),
        )

        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    ######################################################################
    #  L I S T   C U S T O M E R S   T E S T S
    ######################################################################

    def test_list_all_customers(self):
        """It should List all Customers"""

        # Arrange
        customer1 = CustomerFactory()
        customer1.create()

        customer2 = CustomerFactory()
        customer2.create()

        # Act
        response = self.client.get(BASE_URL)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.get_json()

        self.assertEqual(len(data), 2)

        # Verify returned content matches what we created
        user_ids = [c["user_id"] for c in data]
        self.assertIn(customer1.user_id, user_ids)
        self.assertIn(customer2.user_id, user_ids)

    def test_list_customers_empty(self):
        """It should return empty list when no Customers exist"""

        response = self.client.get(BASE_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.get_json()

        self.assertEqual(data, [])

    ######################################################################
    #  U P D A T E   R O O T   U R L   T E S T S
    ######################################################################

    def test_index_contains_service_info(self):
        """It should return service info in JSON format"""

        response = self.client.get("/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.get_json()
        self.assertIsNotNone(data)

        self.assertIn("name", data)
        self.assertIn("message", data)
        self.assertIn("links", data)

        self.assertEqual(data["name"], "Customers Service")

        self.assertIn("customers", data["links"])
        self.assertEqual(data["links"]["customers"], "/customers")

    ######################################################################
    #  E R R O R   H A N D L I N G   T E S T S
    ######################################################################

    def test_method_not_allowed(self):
        """It should return 405 for unsupported methods"""

        response = self.client.patch("/customers")

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_read_customer_internal_server_error(self):
        """It should return 500 when an unexpected server error occurs"""

        original_testing = app.config["TESTING"]
        app.config["TESTING"] = False
        try:
            user_id = "test-user"
            with patch(
                "service.routes.Customer.find", side_effect=Exception("Database error")
            ):
                response = self.client.get(f"{BASE_URL}/{user_id}")
                self.assertEqual(
                    response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        finally:
            app.config["TESTING"] = original_testing

    def test_create_app_database_error(self):
        """It should exit with code 4 when database creation fails"""

        with patch(
            "service.models.db.create_all", side_effect=Exception("DB init error")
        ):
            with patch("sys.exit") as mock_exit:
                mock_exit.side_effect = SystemExit
                with self.assertRaises(SystemExit):
                    create_app()
