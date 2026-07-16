
"""
Paypack API service layer.
Handles communication with Paypack Rwanda Mobile Money API (v1).

Documentation reference: https://docs.paypack.rw

Key facts about the Paypack API:
  * Auth:  POST /auth/agents/authorize  -> {"access": "TOKEN", "refresh": "REFRESH_TOKEN", "expires": "..."}
  * Cashin: POST /transactions/cashin -> body is {"amount": 50000, "number": "078xxxxxxx"}
  * Status: GET /transactions/{ref} -> body is {"status": "success", "data": {...}}
  * Webhook: Paypack POSTs an envelope {"event": "transaction.update", "data": {...}}
            where data contains: client_transaction_id, ref, external_reference,
            status, amount, phone, timestamp.
The responses are handled here.
"""
import uuid
import logging
import requests
from django.conf import settings

logger = logging.getLogger('payments')


class PaypackError(Exception):
    pass


def _get_base_url():
    return "https://payments.paypack.rw/api"


def _get_credentials():
    client_id = getattr(settings, "PAYPACK_CLIENT_ID", "")
    client_secret = getattr(settings, "PAYPACK_CLIENT_SECRET", "")
    if not client_id or not client_secret:
        raise PaypackError("Paypack credentials are not configured.")
    return client_id, client_secret


def get_access_token():
    """Get a fresh Paypack access token using client credentials."""
    client_id, client_secret = _get_credentials()
    url = f"{_get_base_url()}/auth/agents/authorize"
    try:
        resp = requests.post(
            url,
            json={"client_id": client_id, "client_secret": client_secret},
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        raise PaypackError(f"Failed to get Paypack access token: {e}")
    except ValueError as e:
        raise PaypackError(f"Invalid Paypack auth response: {e}")

    token = data.get("access")
    if not token:
        raise PaypackError("Paypack auth response did not contain an access token.")
    return token


def initiate_payment(phone_number, amount, reference, description="", callback_url=None, metadata=None):
    """
    Initiate a mobile money payment request (cashin) via Paypack.
    
    Args:
        phone_number: Mobile number in 07xxxxxxxx format
        amount: Amount in RWF as Decimal or int
        reference: Our internal receipt number (used as Idempotency-Key)
        description: Description of payment (for logging)
        callback_url: Webhook URL for Paypack to call
        metadata: Dict with extra data (student_id, fee_type, etc.) for tracking

    Returns a dict with the server-side transaction identifiers:
        {
            "client_transaction_id": str,
            "reference": str,           # echoes back the reference we sent
            "status": str,              # usually "pending"
            "amount": int,
            "phone": str,
        }
    """
    client_id, client_secret = _get_credentials()

    try:
        token = get_access_token()
        url = f"{_get_base_url()}/transactions/cashin"
        
        # Build request body with database data
        payload = {
            "number": phone_number,
            "amount": int(float(amount)),
        }
        
        # If metadata is provided, include it for tracking (as string for reference)
        if metadata:
            # Store metadata info in logging/audit trail
            logger.info(f"Payment metadata: {metadata}")

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Idempotency-Key": reference or str(uuid.uuid4()),
        }
        
        logger.info(f"PayPack Request - Phone: {phone_number}, Amount: {payload['amount']}, Ref: {reference}, Desc: {description}")
        
        resp = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=15,
        )

        # Log response
        logger.info(f"PayPack Response - Status: {resp.status_code}, Body: {resp.text}")

        resp.raise_for_status()
        body = resp.json()
    except requests.RequestException as e:
        logger.error(f"PayPack payment request failed: {str(e)}")
        raise PaypackError(f"Paypack payment request failed: {e}")
    except ValueError as e:
        logger.error(f"Invalid Paypack response: {str(e)}")
        raise PaypackError(f"Invalid Paypack cashin response: {e}")

    # Paypack returns the cashin result directly (not wrapped in "data"):
    #   {"amount": 1000, "ref": "...", "status": "pending", ...}
    data = body
    api_status = (body.get("status") or "").lower()

    if api_status not in (None, "", "success", "pending", "accepted"):
        error_msg = body.get('message', body.get('detail', body.get('error', api_status)))
        logger.warning(f"PayPack rejected payment: {error_msg}")
        raise PaypackError(
            f"Paypack rejected the payment: {error_msg}"
        )

    client_transaction_id = data.get("ref", "")
    returned_reference = data.get("reference", reference) or reference

    logger.info(f"Payment initiated successfully - Ref: {client_transaction_id}, Status: {api_status}")

    return {
        "client_transaction_id": client_transaction_id,
        "reference": returned_reference,
        "status": api_status or "pending",
        "amount": data.get("amount", int(float(amount))),
        "phone": data.get("phone", phone_number),
    }


def get_transaction_status(ref):
    """
    Look up the status of a transaction by its Paypack reference.

    Returns the inner data dict which includes at least a "status" key
    (pending | successful | failed | cancelled).
    """
    try:
        token = get_access_token()
        url = f"{_get_base_url()}/transactions/find/{ref}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        body = resp.json()
    except requests.RequestException as e:
        raise PaypackError(f"Failed to verify transaction: {e}")
    except ValueError as e:
        raise PaypackError(f"Invalid Paypack transaction response: {e}")

    return body.get("data", {}) or {}


def parse_webhook_payload(raw_body):
    """
    Normalise a Paypack webhook payload (or a flat status dict) into a
    consistent structure:
        {
            "event": str,
            "ref": str,                  # Paypack internal ref
            "client_transaction_id": str,
            "external_reference": str,   # the reference WE sent (receipt number)
            "status": str,               # pending|successful|failed|cancelled
            "amount": number,
            "phone": str,
        }
    """
    if isinstance(raw_body, (bytes, bytearray, str)):
        import json

        try:
            data = json.loads(raw_body)
        except (ValueError, TypeError):
            return {}
    else:
        data = raw_body or {}

    # Paypack wraps webhooks in {"event": ..., "data": {...}}
    if "data" in data and isinstance(data["data"], dict):
        inner = data["data"]
        event = data.get("event", "")
    else:
        inner = data
        event = ""

    status = (inner.get("status") or "").lower()
    return {
        "event": event,
        "ref": inner.get("ref") or inner.get("reference") or inner.get("client_transaction_id") or "",
        "client_transaction_id": inner.get("client_transaction_id") or inner.get("ref") or inner.get("id") or "",
        "external_reference": inner.get("external_reference") or inner.get("reference") or "",
        "status": status,
        "amount": inner.get("amount", 0),
        "phone": inner.get("phone") or inner.get("msisdn") or "",
    }