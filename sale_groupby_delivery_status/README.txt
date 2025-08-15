
Sale: Group By Delivery Status (Odoo 17)
----------------------------------------
- Adds "Delivery Status" under Group By in the Sales -> Quotations/Orders search view.
- Uses group_expand so all selection values appear in the dropdown.
- Depends on sale_management.

If your x_delivery_status comes from another module (e.g., Studio), remove the
field definition in models/sale_order.py but keep the _group_expand method.
