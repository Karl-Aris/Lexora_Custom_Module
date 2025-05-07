odoo.define('custom_sales_order_search', function (require) {
    var rpc = require('web.rpc');
    var core = require('web.core');
    var QWeb = core.qweb;

    var Widget = require('web.Widget');

    var CustomSalesOrderSearch = Widget.extend({
        template: 'custom_search_template',

        events: {
            'click #custom_search_button': 'onSearchClick',
        },

        onSearchClick: function () {
            // Get the input list and split it by commas
            var searchText = $('#custom_search_input').val();
            var salesOrders = searchText.split(',').map(function (so) {
                return so.trim();  // Remove extra spaces
            });

            // Perform the search on the Sales Order model
            rpc.query({
                model: 'sale.order',
                method: 'search_read',
                args: [[['name', 'in', salesOrders]], ['name', 'date_order', 'partner_id']],
            }).then(function (orders) {
                console.log(orders);  // Display results in the console or update the UI
                // Optionally, you can show the results directly in the UI
                // For example, you could render a list below the input field.
            });
        },
    });

    core.action_registry.add('custom_sales_order_search_widget', CustomSalesOrderSearch);
});

