"""
HDEV Payment Gateway service layer.
Handles communication with HDEV Payment API.

Documentation reference: Provided by user (HDEV PAYMENT GATEWAY)

Key facts about the HDEV API:
  * Base URL: https://payment.hdevtech.cloud/api_pay/api/{api_id}/{api_key}
  * Initiate: POST with ref=pay, tel, tx_ref, amount, link
  * Query: POST with ref=read, tx_ref
  * Webhook: HDEV POSTs to the callback URL (link) with transaction result
"""

import uuid
import logging
import requests
from django.conf import settings

logger = logging.getLogger('payments')


class PaymentGatewayError(Exception):
    pass


def _get_base_url():
    api_id = getattr(settings, "HDEV_API_ID", "")
    api_key = getattr(settings, "HDEV_API_KEY", "")
    if not api_id or not api_key:
        raise PaymentGatewayError("HDEV API credentials are not configured.")
    return f"https://payment.hdevtech.cloud/api_pay/api/{api_id}/{api_key}"


def initiate_payment(phone_number, amount, reference, description="", callback_url=None, metadata=None):
    """
    Initiate a mobile money payment request via HDEV.
    
    Args:
        phone_number: Mobile number in 07xxxxxxxx format
        amount: Amount in RWF as Decimal or int
        reference: Our internal receipt number (used as tx_ref)
        description: Description of payment (for logging)
        callback_url: Webhook URL for HDEV to call (the 'link' parameter)
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
    base_url = _get_base_url()
    webhook_url = callback_url or getattr(settings, "HDEV_WEBHOOK_URL", "")
    
    payload = {
        "ref": "pay",
        "tel": phone_number,
        "tx_ref": reference,
        "amount": int(float(amount)),
        "link": webhook_url,
    }
    
    if metadata:
        logger.info(f"Payment metadata: {metadata}")
    
    logger.info(f"HDEV Request - Phone: {phone_number}, Amount: {payload['amount']}, Ref: {reference}, Desc: {description}")
    
    try:
        resp = requests.post(
            base_url,
            data=payload,
            headers={"Accept": "application/json"},
            timeout=30,
        )
        logger.info(f"HDEV Response - Status: {resp.status_code}, Body: {resp.text}")
        body = resp.json()
        logger.info(f"HDEV Response JSON: {body}")
        resp.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"HDEV payment request failed: {str(e)}")
        raise PaymentGatewayError(f"HDEV payment request failed: {e}")
    except ValueError as e:
        logger.error(f"Invalid HDEV response: {str(e)}")
        raise PaymentGatewayError(f"Invalid HDEV payment response: {e}")
    
    data = body
    api_status = (body.get("status") or "").lower()
    
    if api_status not in (None, "", "success", "pending", "accepted"):
        error_msg = body.get('message', body.get('detail', body.get('error', api_status)))
        logger.warning(f"HDEV rejected payment: {error_msg}")
        raise PaymentGatewayError(
            f"HDEV rejected the payment: {error_msg}"
        )
    
    client_transaction_id = data.get("tx_ref", reference)
    
    logger.info(f"Payment initiated successfully - Ref: {client_transaction_id}, Status: {api_status}")
    
    return {
        "client_transaction_id": client_transaction_id,
        "reference": reference,
        "status": api_status or "pending",
        "amount": data.get("amount", int(float(amount))),
        "phone": data.get("tel", phone_number),
    }


def get_transaction_status(ref):
    """
    Look up the status of a transaction by its HDEV reference.
    
    Returns the response dict which includes at least a "status" key
    (pending | successful | failed | cancelled).
    """
    base_url = _get_base_url()
    payload = {
        "ref": "read",
        "tx_ref": ref,
    }
    
    try:
        resp = requests.post(
            base_url,
            data=payload,
            headers={"Accept": "application/json"},
            timeout=10,
        )
        resp.raise_for_status()
        body = resp.json()
    except requests.RequestException as e:
        raise PaymentGatewayError(f"Failed to verify transaction: {e}")
    except ValueError as e:
        raise PaymentGatewayError(f"Invalid HDEV transaction response: {e}")
    
    return body


def parse_webhook_payload(raw_body):
    """
    Normalise an HDEV webhook payload into a consistent structure:
        {
            "event": str,
            "ref": str,                  # HDEV internal ref
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
    
    # HDEV webhook format is not fully documented, so handle common formats
    status = (data.get("status") or "").lower()
    
    return {
        "event": data.get("event", ""),
        "ref": data.get("tx_ref") or data.get("ref") or data.get("id") or "",
        "client_transaction_id": data.get("tx_ref") or data.get("ref") or data.get("id") or "",
        "external_reference": data.get("external_reference") or data.get("reference") or "",
        "status": status,
        "amount": data.get("amount", 0),
        "phone": data.get("tel") or data.get("phone") or data.get("msisdn") or "",
    }
