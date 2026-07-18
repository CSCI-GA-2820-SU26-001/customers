$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with customer data
    function update_form_data(customer) {
        $("#customer_user_id").val(customer.user_id);
        $("#customer_first_name").val(customer.first_name);
        $("#customer_last_name").val(customer.last_name);
        $("#customer_address").val(customer.address);
    }

    // Clears all form fields
    function clear_form_data() {
        $("#customer_user_id").val("");
        $("#customer_first_name").val("");
        $("#customer_last_name").val("");
        $("#customer_address").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // List Customers
    // ****************************************

    $("#list-btn").click(function () {

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: "/api/customers",
            contentType: "application/json",
            data: ""
        });

        ajax.done(function (res) {

            $("#search_results").empty();

            let table = '<table class="table table-striped">';
            table += '<thead>';
            table += '<tr>';
            table += '<th>User ID</th>';
            table += '<th>First Name</th>';
            table += '<th>Last Name</th>';
            table += '<th>Address</th>';
            table += '</tr>';
            table += '</thead><tbody>';

            let firstCustomer = null;

            for (let i = 0; i < res.length; i++) {

                let customer = res[i];

                table += `
                    <tr id="row_${i}">
                        <td>${customer.user_id}</td>
                        <td>${customer.first_name}</td>
                        <td>${customer.last_name}</td>
                        <td>${customer.address}</td>
                    </tr>
                `;

                if (i === 0) {
                    firstCustomer = customer;
                }
            }

            table += "</tbody></table>";

            $("#search_results").append(table);

            if (firstCustomer) {
                update_form_data(firstCustomer);
            }

            flash_message("Success");
        });

        ajax.fail(function (res) {

            if (res.responseJSON && res.responseJSON.message) {
                flash_message(res.responseJSON.message);
            } else {
                flash_message("Unable to retrieve customers.");
            }

        });

    });

    // ****************************************
    // Placeholders for future stories
    // ****************************************

        // ****************************************
    // Create a Customer
    // ****************************************

    $("#create-btn").click(function () {

        $("#flash_message").empty();

        let customer = {
            "user_id": $("#customer_user_id").val(),
            "first_name": $("#customer_first_name").val(),
            "last_name": $("#customer_last_name").val(),
            "address": $("#customer_address").val()
        };

        let ajax = $.ajax({
            type: "POST",
            url: "/api/customers",
            contentType: "application/json",
            data: JSON.stringify(customer)
        });

        ajax.done(function (res) {

            $("#search_results").empty();

            let table = '<table class="table table-striped">';
            table += '<thead>';
            table += '<tr>';
            table += '<th>User ID</th>';
            table += '<th>First Name</th>';
            table += '<th>Last Name</th>';
            table += '<th>Address</th>';
            table += '</tr>';
            table += '</thead><tbody>';

            table += `
                <tr>
                    <td>${res.user_id}</td>
                    <td>${res.first_name}</td>
                    <td>${res.last_name}</td>
                    <td>${res.address}</td>
                </tr>
            `;

            table += "</tbody></table>";

            $("#search_results").append(table);

            update_form_data(res);
            flash_message("Success");
        });

        ajax.fail(function (res) {

            if (res.responseJSON && res.responseJSON.message) {
                flash_message(res.responseJSON.message);
            } else if (res.responseJSON && res.responseJSON.error) {
                flash_message(res.responseJSON.error);
            } else {
                flash_message("Unable to create customer.");
            }

        });

    });

    $("#retrieve-btn").click(function () {
        flash_message("Retrieve not implemented yet.");
    });

    $("#update-btn").click(function () {
        flash_message("Update not implemented yet.");
    });

    $("#delete-btn").click(function () {
        flash_message("Delete not implemented yet.");
    });

    $("#query-btn").click(function () {
        flash_message("Query not implemented yet.");
    });

    $("#suspend-btn").click(function () {
        flash_message("Suspend not implemented yet.");
    });

    $("#clear-btn").click(function () {
        clear_form_data();
        $("#search_results").empty();
        $("#flash_message").empty();
    });

});