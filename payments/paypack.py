"""
Paypack API service layer.
Handles communication with Paypack Rwanda Mobile Money API.
"""
import requests
from django.conf import settings


class PaypackError(Exception):
    pass


def _get_base_url():
    return "https://api.paypack.rw/api/v1" if settings.PAYPACK_ENV == "production" else "https://api.sandbox.paypack.rw/api/v1"


def get_access_token():
    """Get or refresh Paypack access token using client credentials."""
    url = f"{_get_base_url()}/auth/access-token"
    try:
        resp = requests.post(url, json={
            "client_id": settings.PAYPACK_CLIENT_ID,
            "client_secret": settings.PAYPACK_CLIENT_SECRET,
        }, headers={"Content-Type": "application/json", "Accept": "application/json"}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data.get("access")
    except requests.RequestException as e:
        raise PaypackError(f"Failed to get Paypack access token: {e}")


def initiate_payment(phone_number, amount, reference, description=""):
    """
    Initiate a mobile money payment request via Paypack.
    Returns the transaction reference from Paypack.
    """
    if not getattr(settings, "PAYPACK_CLIENT_ID", "") or not getattr(settings, "PAYPACK_CLIENT_SECRET", ""):
        raise PaypackError("Paypack credentials are not configured.")

    try:
        token = get_access_token()
        url = f"{_get_base_url()}/transactions/cashin"
        payload = {
            "phone": phone_number,
            "amount": int(float(amount)),
            "reference": reference,
            "description": description or "School fee payment",
        }
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        resp = requests.post(url, json=payload, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        return data
    except requests.RequestException as e:
        raise PaypackError(f"Paypack payment request failed: {e}")


def verify_transaction(transaction_ref):
    """Verify a transaction status from Paypack."""
    try:
        token = get_access_token()
        url = f"{_get_base_url()}/transactions/{transaction_ref}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        raise PaypackError(f"Failed to verify transaction: {e}")
