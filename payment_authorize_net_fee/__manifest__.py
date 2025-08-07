
{
    "name": "Authorize.Net Surcharge for Website",
    "version": "1.0",
    "summary": "Adds a 3.5% surcharge when Authorize.Net is selected as payment method",
    "category": "Website",
    "depends": ["website_sale", "payment_authorize_net"],
    "data": ["data/auth_net_fee_product.xml"],
    "installable": True,
    "application": False,
}
