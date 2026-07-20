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

# pylint: disable=function-redefined, missing-function-docstring, not-callable
# flake8: noqa
"""
Web Steps

Steps file for web interactions with Selenium

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""

import re
import time
import uuid
import logging
from typing import Any
from behave import when, then  # pylint: disable=no-name-in-module
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions

ID_PREFIX = "customer_"


def save_screenshot(context: Any, filename: str) -> None:
    """Takes a snapshot of the web page for debugging and validation

    Args:
        context (Any): The session context
        filename (str): The message that you are looking for
    """
    # Remove all non-word characters (everything except numbers and letters)
    filename = re.sub(r"[^\w\s]", "", filename)
    # Replace all runs of whitespace with a single dash
    filename = re.sub(r"\s+", "-", filename)
    context.driver.save_screenshot(f"./captures/{filename}.png")


@when('I visit the "Home Page"')
def step_impl(context: Any) -> None:
    """Make a call to the base URL"""
    context.driver.get(context.base_url)
    # Uncomment next line to take a screenshot of the web page
    # save_screenshot(context, 'Home Page')


@then('I should see "{message}" in the title')
def step_impl(context: Any, message: str) -> None:
    """Check the document title for a message"""
    assert message in context.driver.title


@then('I should not see "{text_string}"')
def step_impl(context: Any, text_string: str) -> None:
    element = context.driver.find_element(By.TAG_NAME, "body")
    assert text_string not in element.text


@when('I set the "{element_name}" to "{text_string}"')
def step_impl(context: Any, element_name: str, text_string: str) -> None:
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = context.driver.find_element(By.ID, element_id)
    element.clear()
    element.send_keys(text_string)


@when('I select "{text}" in the "{element_name}" dropdown')
def step_impl(context: Any, text: str, element_name: str) -> None:
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = Select(context.driver.find_element(By.ID, element_id))
    element.select_by_visible_text(text)


@then('I should see "{text}" in the "{element_name}" dropdown')
def step_impl(context: Any, text: str, element_name: str) -> None:
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = Select(context.driver.find_element(By.ID, element_id))
    assert element.first_selected_option.text == text


@then('the "{element_name}" field should be empty')
def step_impl(context: Any, element_name: str) -> None:
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = context.driver.find_element(By.ID, element_id)
    assert element.get_attribute("value") == ""


##################################################################
# These two function simulate copy and paste
##################################################################
@when('I copy the "{element_name}" field')
def step_impl(context: Any, element_name: str) -> None:
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    context.clipboard = element.get_attribute("value")
    logging.info("Clipboard contains: %s", context.clipboard)


@when('I paste the "{element_name}" field')
def step_impl(context: Any, element_name: str) -> None:
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(context.clipboard)


##################################################################
# This code works because of the following naming convention:
# The buttons have an id in the html hat is the button text
# in lowercase followed by '-btn' so the Clear button has an id of
# id='clear-btn'. That allows us to lowercase the name and add '-btn'
# to get the element id of any button
##################################################################


@when('I press the "{button}" button')
def step_impl(context: Any, button: str) -> None:
    button_id = button.lower().replace(" ", "_") + "-btn"
    context.driver.find_element(By.ID, button_id).click()


@then('I should see the "{field_name}" field')
def step_impl(context: Any, field_name: str) -> None:
    """Verify an input field exists on the page."""
    element_id = ID_PREFIX + field_name.lower().replace(" ", "_")
    element = context.driver.find_element(By.ID, element_id)
    assert element.is_displayed()


@then("I should see the results panel")
def step_impl(context: Any) -> None:
    """Verify the shared results panel exists."""
    element = context.driver.find_element(By.ID, "search_results")
    assert element.is_displayed()


@then('I should see "{name}" in the results')
def step_impl(context: Any, name: str) -> None:
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, "search_results"), name
        )
    )
    assert found


@then('I should not see "{name}" in the results')
def step_impl(context: Any, name: str) -> None:
    element = context.driver.find_element(By.ID, "search_results")
    assert name not in element.text


@then('I should see the message "{message}"')
def step_impl(context: Any, message: str) -> None:
    # Uncomment next line to take a screenshot of the web page for debugging
    # save_screenshot(context, message)
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, "flash_message"), message
        )
    )
    assert found


##################################################################
# This code works because of the following naming convention:
# The id field for text input in the html is the element name
# prefixed by ID_PREFIX so the Name field has an id='customer_name'
# We can then lowercase the name and prefix with customer_ to get
# the id
##################################################################


@then('I should see "{text_string}" in the "{element_name}" field')
def step_impl(context: Any, text_string: str, element_name: str) -> None:
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element_value(
            (By.ID, element_id), text_string
        )
    )
    assert found


@when('I change "{element_name}" to "{text_string}"')
def step_impl(context: Any, element_name: str, text_string: str) -> None:
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(text_string)


@when("I create a unique customer through the UI")
def step_impl(context: Any) -> None:
    """Create a unique customer using only the web UI."""
    unique_id = f"bdd-create-{int(time.time() * 1000)}"

    context.customer = {
        "user_id": unique_id,
        "first_name": "Jane",
        "last_name": "Doe",
        "address": "123 Create Street",
    }

    fields = {
        "User Id": context.customer["user_id"],
        "First Name": context.customer["first_name"],
        "Last Name": context.customer["last_name"],
        "Address": context.customer["address"],
    }

    for field_name, value in fields.items():
        element_id = ID_PREFIX + field_name.lower().replace(" ", "_")
        element = context.driver.find_element(By.ID, element_id)
        element.clear()
        element.send_keys(value)

    context.driver.find_element(By.ID, "create-btn").click()


@when('I leave the "{element_name}" field empty')
def step_impl(context: Any, element_name: str) -> None:
    """Clear a field using only the web UI."""
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = context.driver.find_element(By.ID, element_id)
    element.clear()


@then("I should see the created customer in the results")
def step_impl(context: Any) -> None:
    """Verify that the created customer appears in the results panel."""
    results = context.driver.find_element(By.ID, "search_results").text

    assert context.customer["user_id"] in results
    assert context.customer["first_name"] in results
    assert context.customer["last_name"] in results
    assert context.customer["address"] in results


@then("I should see an error message")
def step_impl(context: Any) -> None:
    """Verify that an error message is shown without crashing the page."""
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        lambda driver: driver.find_element(By.ID, "flash_message").text.strip() != ""
    )

    assert found

    message = context.driver.find_element(By.ID, "flash_message").text
    assert "Internal Server Error" not in message
    assert message != "Success"


@when('I set the "User Id" to the created customer user id')
def step_impl(context: Any) -> None:
    """Set the User Id field to the user_id of the customer created through the UI."""
    element = context.driver.find_element(By.ID, "customer_user_id")
    element.clear()
    element.send_keys(context.customer["user_id"])


@then("I should not see the created customer in the results")
def step_impl(context: Any) -> None:
    """Verify that the created customer no longer appears in the results panel."""
    results = context.driver.find_element(By.ID, "search_results").text

    assert context.customer["user_id"] not in results
    
    
@when("I create the following customers through the UI")
def step_impl(context: Any) -> None:
    """Create multiple customers through the web UI."""

    # Generate one unique suffix for this scenario
    suffix = uuid.uuid4().hex[:8]

    for row in context.table:

        user_id = f'{row["user_id"]}-{suffix}'

        fields = {
            "User Id": user_id,
            "First Name": row["first_name"],
            "Last Name": row["last_name"],
            "Address": row["address"],
        }

        for field_name, value in fields.items():
            element_id = ID_PREFIX + field_name.lower().replace(" ", "_")
            element = context.driver.find_element(By.ID, element_id)
            element.clear()
            element.send_keys(value)

        context.driver.find_element(By.ID, "create-btn").click()

        WebDriverWait(context.driver, context.wait_seconds).until(
            expected_conditions.text_to_be_present_in_element(
                (By.ID, "flash_message"),
                "Success",
            )
        )

        context.driver.find_element(By.ID, "clear-btn").click()
