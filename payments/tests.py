from django.test import TestCase


class PaypackIntegrationTests(TestCase):
    def test_paypack_module_imports(self):
        import payments.paypack

        self.assertTrue(hasattr(payments.paypack, 'initiate_payment'))
        self.assertTrue(hasattr(payments.paypack, 'get_transaction_status'))
        self.assertTrue(hasattr(payments.paypack, 'get_access_token'))
        self.assertTrue(hasattr(payments.paypack, 'parse_webhook_payload'))

    def test_parse_webhook_payload_nested(self):
        from payments.paypack import parse_webhook_payload

        body = {
            "event": "transaction.update",
            "data": {
                "client_transaction_id": "pay_123",
                "ref": "pay_123",
                "external_reference": "RCP-20240101-ABC123",
                "status": "successful",
                "amount": 5000,
                "phone": "2507xxxxxxx",
            },
        }
        parsed = parse_webhook_payload(body)
        self.assertEqual(parsed["status"], "successful")
        self.assertEqual(parsed["external_reference"], "RCP-20240101-ABC123")
        self.assertEqual(parsed["client_transaction_id"], "pay_123")

    def test_parse_webhook_payload_flat(self):
        from payments.paypack import parse_webhook_payload

        parsed = parse_webhook_payload({"reference": "RCP-X", "status": "failed", "id": "pay_9"})
        self.assertEqual(parsed["status"], "failed")
        self.assertEqual(parsed["ref"], "RCP-X")
        self.assertEqual(parsed["client_transaction_id"], "pay_9")
        self.assertEqual(parsed["external_reference"], "RCP-X")
