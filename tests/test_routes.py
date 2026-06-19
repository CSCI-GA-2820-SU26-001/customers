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
