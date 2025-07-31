{
    "name": "Mock Authorize.Net Provider (Working)",
    "version": "1.0",
    "category": "Accounting",
    "summary": "Mock Authorize.Net for testing surcharge logic in Sales Order Portal",
    "description": "Simulates Authorize.Net using 'transfer' as base provider for testing in staging.",
    "depends": ["payment"],
    "data": ["data/mock_authorize_net.xml"],
    "installable": True,
    "application": False,
}
