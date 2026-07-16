@list
Feature: Customer Administration

  As an eCommerce manager
  I need a web page to manage customers
  So that I can view all customers in the system

  Background:
    Given the following customers
      | user_id | first_name | last_name | address |
      | C001    | John       | Smith     | New York |
      | C002    | Alice      | Brown     | Boston |
      | C003    | Bob        | Johnson   | San Francisco |

  Scenario: List all customers

    When I visit the "Home Page"

    Then I should see "Customer Administration" in the title

    When I press the "List" button

    Then I should see "John" in the results

    And I should see "Alice" in the results

    And I should see "Bob" in the results