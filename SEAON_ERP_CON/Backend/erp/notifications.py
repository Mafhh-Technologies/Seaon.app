"""Order notifications through SMTP email and the WhatsApp Cloud API.

Credentials are read from environment variables; never commit real credentials.
Notifications are best-effort: an external provider outage does not undo an order.
"""
import json
import os
import re
import urllib.error
import urllib.request
from django.conf import settings
from django.core.mail import send_mail


def _send_vendor_email(order):
    if not order.vendor_email:
        return {"status": "skipped", "detail": "No vendor email supplied."}
    if not settings.EMAIL_HOST or not settings.DEFAULT_FROM_EMAIL:
        return {"status": "not_configured", "detail": "Configure SMTP settings in .env."}
    subject = f"New SEAON purchase/order request: {order.order_number}"
    message = (
        f"Hello,\n\nA new order has been created in SEAON ERP.\n\n"
        f"Order: {order.order_number}\nProduct: {order.product.name}\n"
        f"SKU: {order.product.sku}\nQuantity: {order.quantity} {order.product.unit}\n"
        f"Order type: {order.order_type}\nStatus: {order.status}\n"
        f"Notes: {order.notes or 'None'}\n\nPlease contact us to confirm availability and delivery.\n\nSEAON ERP"
    )
    try:
        sent = send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [order.vendor_email], fail_silently=False)
        return {"status": "sent" if sent else "failed", "detail": "Email accepted by SMTP." if sent else "SMTP did not send the email."}
    except Exception as exc:
        return {"status": "failed", "detail": f"Email provider error: {exc.__class__.__name__}. Check SMTP configuration."}


def _send_vendor_whatsapp(order):
    recipient = re.sub(r"[^0-9]", "", order.vendor_whatsapp or "")
    if not recipient:
        return {"status": "skipped", "detail": "No vendor WhatsApp number supplied."}
    token = os.getenv("WHATSAPP_ACCESS_TOKEN", "").strip()
    phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "").strip()
    api_version = os.getenv("WHATSAPP_API_VERSION", "v23.0").strip()
    if not token or not phone_number_id:
        return {"status": "not_configured", "detail": "Configure WhatsApp Cloud API credentials in .env."}
    text = (
        f"SEAON ERP: New order {order.order_number}\nProduct: {order.product.name} ({order.product.sku})\n"
        f"Quantity: {order.quantity} {order.product.unit}\nType: {order.order_type}\n"
        f"Status: {order.status}\nNotes: {order.notes or 'None'}"
    )
    payload = {"messaging_product": "whatsapp", "recipient_type": "individual", "to": recipient,
               "type": "text", "text": {"preview_url": False, "body": text}}
    url = f"https://graph.facebook.com/{api_version}/{phone_number_id}/messages"
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), method="POST",
                                 headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            data = json.loads(response.read().decode("utf-8"))
            if response.status in (200, 201) and data.get("messages"):
                return {"status": "sent", "detail": "WhatsApp API accepted the message."}
            return {"status": "failed", "detail": "WhatsApp API did not confirm delivery."}
    except urllib.error.HTTPError as exc:
        # Do not expose provider response bodies, which can contain sensitive details.
        return {"status": "failed", "detail": f"WhatsApp API returned HTTP {exc.code}. Check recipient, token, permissions and message policy."}
    except Exception as exc:
        return {"status": "failed", "detail": f"WhatsApp provider error: {exc.__class__.__name__}. Check network and configuration."}


def notify_vendor_for_order(order):
    """Attempt both channels and return a safe status summary."""
    return {"email": _send_vendor_email(order), "whatsapp": _send_vendor_whatsapp(order)}
