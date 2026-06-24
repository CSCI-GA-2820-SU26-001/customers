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
        }

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

            if not isinstance(self.user_id, str) or not self.user_id.strip():
                raise TypeError("user_id must be a non-empty string")

            if not isinstance(self.first_name, str) or not self.first_name.strip():
                raise TypeError("first_name must be a non-empty string")

            if not isinstance(self.last_name, str) or not self.last_name.strip():
                raise TypeError("last_name must be a non-empty string")

            if not isinstance(self.address, str) or not self.address.strip():
                raise TypeError("address must be a non-empty string")

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
