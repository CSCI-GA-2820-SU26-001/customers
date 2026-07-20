Feature: Customer Administration

  As an eCommerce manager
  I need a web page to manage customers
  So that I can view all customers in the system

  # Background:
  #   Given the following customers
  #     | user_id | first_name | last_name | address |
  #     | C001    | John       | Smith     | New York |
  #     | C002    | Alice      | Brown     | Boston |
  #     | C003    | Bob        | Johnson   | San Francisco |

@list
  Scenario: Display the Customer Administration UI and List Customers
    When I visit the "Home Page"
    Then I should see "Customer Administration" in the title
    And I should see the "User Id" field
    And I should see the "First Name" field
    And I should see the "Last Name" field
    And I should see the "Address" field
    And I should see the results panel
    When I press the "List" button
    Then I should see the message "Success"

  # Scenario: List all customers
  #   When I visit the "Home Page"
  #   And I create the following customers
  #       ...
  #       ...
  #   And I press the "List" button
  #   Then I should see "John" in the results
  #   And I should see "Alice" in the results
  #   And I should see "Bob" in the results

  @create
  Scenario: Create a customer from the admin UI
    When I visit the "Home Page"
    And I create a unique customer through the UI
    Then I should see the message "Success"
    And I should see the created customer in the results

  @create
  Scenario: Create customer with missing required data
    When I visit the "Home Page"
    And I set the "User Id" to "bdd-create-missing"
    And I leave the "First Name" field empty
    And I set the "Last Name" to "Doe"
    And I set the "Address" to "123 Missing Street"
    And I press the "Create" button
    Then I should see an error message
    And I should not see "Internal Server Error"

  @read
  Scenario: Read an existing customer from the admin UI
    When I visit the "Home Page"
    And I create a unique customer through the UI
    Then I should see the message "Success"
    When I press the "Clear" button
    And I set the "User Id" to the created customer user id
    And I press the "Read" button
    Then I should see the message "Success"
    And I should see the created customer in the results

  @read
  Scenario: Read a customer that does not exist
    When I visit the "Home Page"
    And I set the "User Id" to "bdd-read-not-found"
    And I press the "Read" button
    Then I should see the message "Customer not found"
    And I should not see "Internal Server Error"

  @delete
  Scenario: Delete an existing customer from the admin UI
    When I visit the "Home Page"
    And I create a unique customer through the UI
    Then I should see the message "Success"

    When I press the "Clear" button
    And I set the "User Id" to the created customer user id
    And I press the "Delete" button
    Then I should see the message "Success"

    When I press the "Clear" button
    And I press the "List" button
    Then I should not see the created customer in the results

  @delete
  Scenario: Delete a customer that does not exist
    When I visit the "Home Page"
    And I set the "User Id" to "bdd-delete-not-found"
    And I press the "Delete" button
    Then I should see the message "Success"
    And I should not see "Internal Server Error"