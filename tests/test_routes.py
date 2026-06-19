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
TestYourResourceModel API Service Test Suite
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from wsgi import app
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
class TestYourResourceService(TestCase):
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
