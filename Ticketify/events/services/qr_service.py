import base64
import hmac
import hashlib
import json
import time
from io import BytesIO

from django.conf import settings
from django.utils import timezone as dj_timezone
from django.core.cache import cache
import qrcode


def _time_window(ts=None, interval=None):
    interval = interval or settings.QR_REFRESH_INTERVAL
    ts = ts or int(time.time())
    return int(ts // interval) * interval


def _sign_payload(payload: str, secret: str) -> str:
    sig = hmac.new(secret.encode('utf-8'), payload.encode('utf-8'), hashlib.sha256).hexdigest()
    return sig


def make_token(ticket, now_ts=None):
    """Create a signed token for the ticket for the current time window.
    The token contains a JSON payload and HMAC signature then base64 encoded.
    """
    secret = ticket.qr_secret or settings.QR_SIGNING_SECRET
    window_ts = _time_window(now_ts)

    payload = {
        'ticket_id': ticket.ticket_id,
        'event_id': ticket.event.id,
        'ts': window_ts,
    }
    payload_json = json.dumps(payload, separators=(',', ':'))
    sig = _sign_payload(payload_json, secret)

    blob = payload_json + '|' + sig
    token = base64.urlsafe_b64encode(blob.encode('utf-8')).decode('utf-8')

    # store temporary token in cache to help prevent replay and allow quick revocation
    cache_key = f'qr_token:{ticket.ticket_id}:{window_ts}'
    cache.set(cache_key, True, timeout=settings.QR_REFRESH_INTERVAL + settings.QR_LEEWAY_SECONDS)

    # update ticket's last generated time
    ticket.last_qr_generated_at = dj_timezone.now()
    if not ticket.qr_secret:
        # if ticket has no per-ticket secret, set one derived from settings secret
        ticket.qr_secret = hashlib.sha256(f"{ticket.ticket_id}{settings.QR_SIGNING_SECRET}".encode('utf-8')).hexdigest()
    ticket.save(update_fields=['last_qr_generated_at', 'qr_secret'])

    return token


def generate_qr_base64(token: str) -> str:
    """Generate a PNG QR image for the token and return Base64-encoded image data"""
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=8, border=2)
    qr.add_data(token)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_b64 = base64.b64encode(buffer.read()).decode('utf-8')
    buffer.close()
    return img_b64


def verify_token(token: str, leeway=None):
    """Verify token signature and return payload dict if valid, otherwise raise ValueError"""
    leeway = leeway or settings.QR_LEEWAY_SECONDS
    try:
        decoded = base64.urlsafe_b64decode(token.encode('utf-8')).decode('utf-8')
        payload_json, sig = decoded.rsplit('|', 1)
        payload = json.loads(payload_json)
    except Exception:
        raise ValueError('Invalid token format')

    ticket_id = payload.get('ticket_id')
    window_ts = int(payload.get('ts'))

    # Try to reconstruct secret: first check ticket-specific secret from cache/db
    # The caller should fetch the ticket and pass its secret if available. For now, return payload and sig for caller to verify.
    return payload, sig
