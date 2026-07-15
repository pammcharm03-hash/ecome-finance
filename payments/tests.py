from django.test import TestCase


class PaypackIntegrationTests(TestCase):
    def test_paypack_module_imports(self):
        import payments.paypack

        self.assertTrue(hasattr(payments.paypack, 'initiate_payment'))
        self.assertTrue(hasattr(payments.paypack, 'verify_transaction'))
        self.assertTrue(hasattr(payments.paypack, 'get_access_token'))
