"""
Models for Customers

All of the models are stored in this module
"""

import logging
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """Used for data validation errors when deserializing"""


class Customer(db.Model):
    """
    Class that represents a Customer
    """

    ##################################################
    # Table Schema
    ##################################################

    __tablename__ = "customers"

    user_id = db.Column(db.String(63), primary_key=True)
    first_name = db.Column(db.String(63), nullable=False)
    last_name = db.Column(db.String(63), nullable=False)
    address = db.Column(db.String(256), nullable=False)
    suspended = db.Column(db.Boolean(), nullable=False, default=False)

    def __repr__(self):
        return f"<Customer {self.user_id}: {self.first_name} {self.last_name}>"

    def create(self):
        """Creates a Customer in the database"""
        logger.info("Creating customer %s", self.user_id)

        try:
            db.session.add(self)
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            logger.error("Error creating customer: %s", self)
            raise DataValidationError(error) from error

    def update(self):
        """Updates a Customer in the database"""
        logger.info("Saving customer %s", self.user_id)

        try:
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            logger.error("Error updating customer: %s", self)
            raise DataValidationError(error) from error

    def delete(self):
        """Removes a Customer from the database"""
        logger.info("Deleting customer %s", self.user_id)

        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            logger.error("Error deleting customer: %s", self)
            raise DataValidationError(error) from error

    def serialize(self):
        """Serializes a Customer into a dictionary"""
        return {
            "user_id": self.user_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "address": self.address,
            "suspended": bool(self.suspended),
        }

    @staticmethod
    def _validate_non_empty_string(value, field_name):
        """Validates that a field is a non-empty string"""
        if not isinstance(value, str) or not value.strip():
            raise TypeError(f"{field_name} must be a non-empty string")

    @staticmethod
    def _validate_boolean(value, field_name):
        """Validates that a field is a boolean"""
        if not isinstance(value, bool):
            raise TypeError(f"{field_name} must be a boolean")

    def deserialize(self, data):
        """
        Deserializes a Customer from a dictionary

        Args:
            data (dict): A dictionary containing the customer data
        """
        try:
            if not isinstance(data, dict):
                raise TypeError("Invalid data type")

            self.user_id = data["user_id"]
            self.first_name = data["first_name"]
            self.last_name = data["last_name"]
            self.address = data["address"]

            self._validate_non_empty_string(self.user_id, "user_id")
            self._validate_non_empty_string(self.first_name, "first_name")
            self._validate_non_empty_string(self.last_name, "last_name")
            self._validate_non_empty_string(self.address, "address")

            if "suspended" in data:
                self._validate_boolean(data["suspended"], "suspended")
                self.suspended = data["suspended"]
            elif self.suspended is None:
                self.suspended = False

        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid Customer: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Customer: body of request contained bad or no data "
                + str(error)
            ) from error

        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def all(cls):
        """Returns all Customers in the database"""
        logger.info("Processing all customers")
        return cls.query.all()

    @classmethod
    def find(cls, user_id):
        """Finds a Customer by user_id"""
        logger.info("Processing lookup for user_id %s ...", user_id)
        return cls.query.session.get(cls, user_id)

    ##################################################
    # QUERY METHODS
    ##################################################

    @classmethod
    def find_by_first_name(cls, first_name):
        """
        Returns all Customers with the given first name
        """
        logger.info("Processing lookup for first_name %s ...", first_name)
        return cls.query.filter(cls.first_name == first_name).all()

    @classmethod
    def find_by_last_name(cls, last_name):
        """
        Returns all Customers with the given last name
        """
        logger.info("Processing lookup for last_name %s ...", last_name)
        return cls.query.filter(cls.last_name == last_name).all()

    @classmethod
    def find_by_name(cls, first_name, last_name):
        """
        Returns all Customers matching both first and last name
        """
        logger.info(
            "Processing lookup for first_name=%s last_name=%s ...",
            first_name,
            last_name,
        )

        return cls.query.filter(
            cls.first_name == first_name,
            cls.last_name == last_name,
        ).all()
