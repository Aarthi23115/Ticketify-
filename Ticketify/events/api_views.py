from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.conf import settings
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from .serializers import QRValidateSerializer
from .models import Ticket, TicketScanLog
from .services.qr_service import verify_token, make_token, generate_qr_base64
import hmac
import hashlib
import json


class QRValidateAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = QRValidateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']
        device_info = serializer.validated_data.get('device_info', '')
        remote_addr = request.META.get('REMOTE_ADDR')

        # Basic rate limiting per ticket + IP
        # Parse token to get ticket_id
        try:
            payload, sig = verify_token(token)
        except ValueError:
            return Response({'detail': 'Invalid token format'}, status=status.HTTP_400_BAD_REQUEST)

        ticket_id = payload.get('ticket_id')
        event_id = payload.get('event_id')
        ts = int(payload.get('ts'))

        # Rate limit key
        rate_key = f'qr_rate:{ticket_id}:{remote_addr}'
        attempts = cache.get(rate_key) or 0
        if attempts >= 10:
            return Response({'detail': 'Too many attempts'}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        cache.incr(rate_key) if cache.get(rate_key) else cache.set(rate_key, 1, timeout=60)

        ticket = get_object_or_404(Ticket, ticket_id=ticket_id)

        # Verify event matches
        if str(ticket.event.id) != str(event_id):
            TicketScanLog.objects.create(ticket=ticket, success=False, remote_addr=remote_addr, device_info=device_info, notes='Event mismatch')
            return Response({'detail': 'Event mismatch'}, status=status.HTTP_400_BAD_REQUEST)

        # Recompute signature using ticket's secret (fallback to global)
        secret = ticket.qr_secret or settings.QR_SIGNING_SECRET
        payload_json = json.dumps({'ticket_id': ticket.ticket_id, 'event_id': ticket.event.id, 'ts': ts}, separators=(',', ':'))
        expected_sig = hmac.new(secret.encode('utf-8'), payload_json.encode('utf-8'), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected_sig, sig):
            TicketScanLog.objects.create(ticket=ticket, success=False, remote_addr=remote_addr, device_info=device_info, notes='Bad signature')
            return Response({'detail': 'Invalid signature'}, status=status.HTTP_400_BAD_REQUEST)

        # Check timestamp window
        now_ts = int(timezone.now().timestamp())
        # Accept tokens within the configured leeway
        if abs(now_ts - ts) > settings.QR_REFRESH_INTERVAL + settings.QR_LEEWAY_SECONDS:
            TicketScanLog.objects.create(ticket=ticket, success=False, remote_addr=remote_addr, device_info=device_info, notes='Token expired')
            return Response({'detail': 'Token expired'}, status=status.HTTP_400_BAD_REQUEST)

        # Prevent reuse
        if ticket.qr_status == 'USED' or ticket.status == 'used':
            TicketScanLog.objects.create(ticket=ticket, success=False, remote_addr=remote_addr, device_info=device_info, notes='Already used')
            return Response({'detail': 'Ticket already used'}, status=status.HTTP_400_BAD_REQUEST)

        # Prevent duplicate scans in same window
        cache_key = f'qr_scanned:{ticket.ticket_id}:{ts}'
        if cache.get(cache_key):
            TicketScanLog.objects.create(ticket=ticket, success=False, remote_addr=remote_addr, device_info=device_info, notes='Duplicate scan window')
            return Response({'detail': 'Duplicate scan detected'}, status=status.HTTP_400_BAD_REQUEST)

        # Mark as used and log
        ticket.qr_status = 'USED'
        ticket.validated_at = timezone.now()
        ticket.validated_by = None
        ticket.save(update_fields=['qr_status', 'validated_at', 'validated_by'])

        cache.set(cache_key, True, timeout=settings.QR_REFRESH_INTERVAL + settings.QR_LEEWAY_SECONDS)
        TicketScanLog.objects.create(ticket=ticket, success=True, remote_addr=remote_addr, device_info=device_info, notes='Validated')

        return Response({'detail': 'Ticket validated', 'ticket_id': ticket.ticket_id}, status=status.HTTP_200_OK)


class QRGenerateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, ticket_id):
        # Ensure ticket belongs to user (do not change auth flow)
        ticket = get_object_or_404(Ticket, ticket_id=ticket_id, user=request.user)

        # Create token and QR image
        token = make_token(ticket)
        img_b64 = generate_qr_base64(token)

        expires_in = settings.QR_REFRESH_INTERVAL

        return Response({'image_base64': img_b64, 'token': token, 'expires_in': expires_in})
