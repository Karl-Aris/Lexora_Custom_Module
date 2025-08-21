# Carrier Tracking Webhook (Odoo 17)

This module adds webhook-based shipment tracking to Sale Orders.

## Endpoints
- `POST /webhook/carrier/<carrier>` (JSON)
  - Payload fields: `tracking_number` (required), `status` (string)

## Install
1. Copy `carrier_tracking_webhook/` into your Odoo addons path.
2. Update app list and install **Carrier Tracking Webhook**.

## Test (curl)
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"tracking_number":"TEST123","status":"In Transit"}' \
  https://your-odoo.example.com/webhook/carrier/fedex
```
