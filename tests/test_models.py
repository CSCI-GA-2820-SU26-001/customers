######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0
######################################################################

"""
Test cases for Customer Model
"""

# pylint: disable=duplicate-code

import os
import logging
from unittest import TestCase
from unittest.mock import patch

from wsgi import app
from service.models import Customer, DataValidationError, db
from .factories import CustomerFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI",
    "postgresql+psycopg://postgres:postgres@localhost:5432/testdb",
)


######################################################################
# Customer Model Test Cases
######################################################################
# pylint: disable=too-many-public-methods
class TestCustomerModel(TestCase):
    """Test Cases for Customer Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Customer).delete()
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ##################################################################
    # Test Cases
    ##################################################################

    def test_create_a_customer(self):
        """It should create a Customer"""
        customer = CustomerFactory()
        customer.create()

        found = Customer.all()

        self.assertEqual(len(found), 1)
        self.assertEqual(found[0].user_id, customer.user_id)
        self.assertEqual(found[0].first_name, customer.first_name)
        self.assertEqual(found[0].last_name, customer.last_name)
        self.assertEqual(found[0].address, customer.address)

    def test_find_a_customer(self):
        """It should find a Customer by user_id"""
        customer = CustomerFactory()
        customer.create()

        found = Customer.find(customer.user_id)

        self.assertIsNotNone(found)
        self.assertEqual(found.user_id, customer.user_id)
        self.assertEqual(found.first_name, customer.first_name)
        self.assertEqual(found.last_name, customer.last_name)
        self.assertEqual(found.address, customer.address)

    def test_customer_not_found(self):
        """It should not find a Customer that does not exist"""
        found = Customer.find("unknown-user")
        self.assertIsNone(found)

    def test_list_all_customers(self):
        """It should list all Customers"""
        customers = CustomerFactory.create_batch(5)

        for customer in customers:
            customer.create()

        found = Customer.all()

        self.assertEqual(len(found), 5)

    def test_update_a_customer(self):
        """It should update a Customer"""
        customer = CustomerFactory()
        customer.create()

        customer.first_name = "Updated"
        customer.update()

        found = Customer.find(customer.user_id)

        self.assertEqual(found.first_name, "Updated")

    def test_delete_a_customer(self):
        """It should delete a Customer"""
        customer = CustomerFactory()
        customer.create()

        self.assertEqual(len(Customer.all()), 1)

        customer.delete()

        self.assertEqual(len(Customer.all()), 0)

    def test_serialize_a_customer(self):
        """It should serialize a Customer"""
        customer = CustomerFactory()

        data = customer.serialize()

        self.assertEqual(data["user_id"], customer.user_id)
        self.assertEqual(data["first_name"], customer.first_name)
        self.assertEqual(data["last_name"], customer.last_name)
        self.assertEqual(data["address"], customer.address)

    def test_deserialize_a_customer(self):
        """It should deserialize a Customer"""
        data = {
            "user_id": "user123",
            "first_name": "John",
            "last_name": "Doe",
            "address": "123 Main Street",
        }

        customer = Customer()
        customer.deserialize(data)

        self.assertEqual(customer.user_id, "user123")
        self.assertEqual(customer.first_name, "John")
        self.assertEqual(customer.last_name, "Doe")
        self.assertEqual(customer.address, "123 Main Street")

    def test_deserialize_missing_user_id(self):
        """It should not deserialize a Customer with missing user_id"""
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "address": "123 Main Street",
        }

        customer = Customer()

        self.assertRaises(DataValidationError, customer.deserialize, data)

    def test_deserialize_missing_first_name(self):
        """It should not deserialize a Customer with missing first_name"""
        data = {
            "user_id": "user123",
            "last_name": "Doe",
            "address": "123 Main Street",
        }

        customer = Customer()

        self.assertRaises(DataValidationError, customer.deserialize, data)

    def test_deserialize_missing_last_name(self):
        """It should not deserialize a Customer with missing last_name"""
        data = {
            "user_id": "user123",
            "first_name": "John",
            "address": "123 Main Street",
        }

        customer = Customer()

        self.assertRaises(DataValidationError, customer.deserialize, data)

    def test_deserialize_missing_address(self):
        """It should not deserialize a Customer with missing address"""
        data = {
            "user_id": "user123",
            "first_name": "John",
            "last_name": "Doe",
        }

        customer = Customer()

        self.assertRaises(DataValidationError, customer.deserialize, data)

    def test_deserialize_bad_data(self):
        """It should not deserialize bad data"""
        customer = Customer()

        self.assertRaises(DataValidationError, customer.deserialize, None)

    def test_deserialize_empty_user_id(self):
        """It should not deserialize a Customer with empty user_id"""
        data = {
            "user_id": "",
            "first_name": "John",
            "last_name": "Doe",
            "address": "123 Main Street",
        }

        customer = Customer()

        self.assertRaises(DataValidationError, customer.deserialize, data)

    def test_deserialize_empty_first_name(self):
        """It should not deserialize a Customer with empty first_name"""
        data = {
            "user_id": "user123",
            "first_name": "",
            "last_name": "Doe",
            "address": "123 Main Street",
        }

        customer = Customer()

        self.assertRaises(DataValidationError, customer.deserialize, data)

    def test_deserialize_empty_last_name(self):
        """It should not deserialize a Customer with empty last_name"""
        data = {
            "user_id": "user123",
            "first_name": "John",
            "last_name": "",
            "address": "123 Main Street",
        }

        customer = Customer()

        self.assertRaises(DataValidationError, customer.deserialize, data)

    def test_deserialize_empty_address(self):
        """It should not deserialize a Customer with empty address"""
        data = {
            "user_id": "user123",
            "first_name": "John",
            "last_name": "Doe",
            "address": "",
        }

        customer = Customer()

        self.assertRaises(DataValidationError, customer.deserialize, data)

    @patch("service.models.db.session.commit")
    def test_create_database_error(self, exception_mock):
        """It should raise DataValidationError on create database error"""
        exception_mock.side_effect = Exception("database error")
        customer = CustomerFactory()

        self.assertRaises(DataValidationError, customer.create)

    @patch("service.models.db.session.commit")
    def test_update_database_error(self, exception_mock):
        """It should raise DataValidationError on update database error"""
        customer = CustomerFactory()
        customer.create()

        exception_mock.side_effect = Exception("database error")

        self.assertRaises(DataValidationError, customer.update)

    @patch("service.models.db.session.commit")
    def test_delete_database_error(self, exception_mock):
        """It should raise DataValidationError on delete database error"""
        customer = CustomerFactory()
        customer.create()

        exception_mock.side_effect = Exception("database error")

        self.assertRaises(DataValidationError, customer.delete)

    ##################################################
    # QUERY METHODS TESTS
    ##################################################

    def test_find_by_first_name(self):
        """It should find Customers by first name"""

        customer1 = CustomerFactory(
            first_name="John",
            last_name="Smith",
        )
        customer2 = CustomerFactory(
            first_name="John",
            last_name="Brown",
        )
        customer3 = CustomerFactory(
            first_name="Alice",
            last_name="Smith",
        )

        customer1.create()
        customer2.create()
        customer3.create()

        customers = Customer.find_by_first_name("John")

        self.assertEqual(len(customers), 2)

        for customer in customers:
            self.assertEqual(customer.first_name, "John")

    def test_find_by_last_name(self):
        """It should find Customers by last name"""

        customer1 = CustomerFactory(
            first_name="John",
            last_name="Smith",
        )
        customer2 = CustomerFactory(
            first_name="Alice",
            last_name="Smith",
        )
        customer3 = CustomerFactory(
            first_name="Bob",
            last_name="Brown",
        )

        customer1.create()
        customer2.create()
        customer3.create()

        customers = Customer.find_by_last_name("Smith")

        self.assertEqual(len(customers), 2)

        for customer in customers:
            self.assertEqual(customer.last_name, "Smith")

    def test_find_by_name(self):
        """It should find Customers by first and last name"""

        customer1 = CustomerFactory(
            first_name="John",
            last_name="Smith",
        )
        customer2 = CustomerFactory(
            first_name="John",
            last_name="Brown",
        )
        customer3 = CustomerFactory(
            first_name="Alice",
            last_name="Smith",
        )

        customer1.create()
        customer2.create()
        customer3.create()

        customers = Customer.find_by_name("John", "Smith")

        self.assertEqual(len(customers), 1)
        self.assertEqual(customers[0].first_name, "John")
        self.assertEqual(customers[0].last_name, "Smith")

    def test_find_by_name_no_matches(self):
        """It should return an empty list when no Customers match"""

        customer = CustomerFactory()
        customer.create()

        customers = Customer.find_by_name(
            "DoesNotExist",
            "Nobody",
        )

        self.assertEqual(customers, [])
