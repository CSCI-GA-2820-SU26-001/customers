@list
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