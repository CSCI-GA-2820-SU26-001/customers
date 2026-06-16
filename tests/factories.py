"""
Test Factory to make fake objects for testing
"""

import factory
from service.models import Customer


class CustomerFactory(factory.Factory):
    """Creates fake customers for testing"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Customer

    user_id = factory.Sequence(lambda n: f"user{n}")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    address = factory.Faker("street_address")


# Temporary compatibility alias for the original template.
YourResourceModelFactory = CustomerFactory
