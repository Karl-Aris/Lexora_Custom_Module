# returns_report

Example module that for Returns Report.

## Install
1. Copy the `returns_report` folder into your Odoo addons path.
2. Restart Odoo server.
3. Update app list (Apps -> Update Apps List) and search for "Stock Move Line Extension".
4. Install the module.

## Notes
- The example XML assumes the stock module view XML IDs `stock.view_move_line_form` and `stock.view_move_line_tree` exist. If your database uses different IDs, update `views/stock_move_line_views.xml` accordingly.
- Modify business logic (create/write/constraints) to match your exact requirements.
