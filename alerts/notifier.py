"""
Alert dispatch — email via SMTP + SMS via Twilio.
Deduplicates: one notification per event per 30-minute window.
"""
import logging
from datetime import timedelta
from django.conf import settings
from django.utils import timezone

logger       = logging.getLogger(__name__)
DEDUP_WINDOW = timedelta(minutes=30)


def _already_notified(event) -> bool:
    from .models import AlertRecord
    return AlertRecord.objects.filter(event=event, sent_at__gte=timezone.now()-DEDUP_WINDOW).exists()


def _record(event, channel: str):
    from .models import AlertRecord
    AlertRecord.objects.create(event=event, channel=channel)


def send_sms(message: str, to_numbers: list):
    try:
        from twilio.rest import Client
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        for num in filter(None, to_numbers):
            client.messages.create(body=message, from_=settings.TWILIO_FROM_NUMBER, to=num)
            logger.info('SMS -> %s', num)
    except ImportError:
        logger.warning('twilio not installed — SMS skipped')
    except Exception as exc:
        logger.error('SMS error: %s', exc)


def send_email_alert(subject: str, body: str):
    try:
        from django.core.mail import send_mail
        recipients = [e for e in settings.NOC_ALERT_EMAILS if e]
        if recipients:
            send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, recipients)
            logger.info('Alert email -> %s', recipients)
    except Exception as exc:
        logger.error('Email error: %s', exc)


def notify_fault(event) -> bool:
    if _already_notified(event):
        return False
    subject = f'[NetWatch {event.severity.upper()}] {event.device.name}: {event.event_type}'
    body = (
        f'Device:   {event.device.name} ({event.device.ip_address})\n'
        f'Region:   {event.device.region}\n'
        f'Severity: {event.severity}\n'
        f'Event:    {event.event_type}\n'
        f'Message:  {event.message}\n'
        f'Time:     {event.occurred_at:%Y-%m-%d %H:%M:%S %Z}\n'
        f'Detail:   {event.detail}\n'
    )
    send_email_alert(subject, body)
    if event.severity == 'critical':
        send_sms(f'[CRITICAL] {event.device.name}: {event.message}',
                 getattr(settings, 'NOC_SMS_NUMBERS', []))
    _record(event, 'email')
    return True
