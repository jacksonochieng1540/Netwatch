import logging
from celery import shared_task
from django.utils import timezone
from django.conf import settings
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from devices.models import Device
from .models import PollResult, NetworkEvent
from .poller import poll_device

logger       = logging.getLogger(__name__)
channel_layer = get_channel_layer()


def _push_ws_update(data: dict):
    async_to_sync(channel_layer.group_send)('dashboard', {'type': 'device_update', 'data': data})


@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def poll_single_device(self, device_id: int):
    try:
        device = Device.objects.select_related('region').get(pk=device_id, is_active=True)
    except Device.DoesNotExist:
        return

    try:
        data = poll_device(device)
    except Exception as exc:
        raise self.retry(exc=exc)

    poll = PollResult.objects.create(device=device, **data)
    prev = device.status

    if not data['is_reachable']:
        device.mark_down()
    elif (data['packet_loss_pct'] or 0) >= settings.FAULT_PACKET_LOSS_THRESHOLD:
        device.mark_degraded()
    elif (data['latency_ms'] or 0) >= settings.FAULT_LATENCY_THRESHOLD_MS:
        device.mark_degraded()
    else:
        device.mark_up()

    if device.status != prev:
        sev = (NetworkEvent.Severity.CRITICAL if device.status == 'down' else
               NetworkEvent.Severity.WARNING  if device.status == 'warn'  else
               NetworkEvent.Severity.INFO)
        NetworkEvent.objects.create(
            device=device,
            event_type=NetworkEvent.EventType.STATUS_CHANGE,
            severity=sev,
            message=f'{device.name} transitioned {prev} -> {device.status}',
            detail={'prev': prev, 'current': device.status,
                    'latency_ms': data['latency_ms'], 'loss_pct': data['packet_loss_pct']},
        )

    if (data['latency_ms'] or 0) >= settings.FAULT_LATENCY_THRESHOLD_MS and device.status == 'up':
        NetworkEvent.objects.create(
            device=device,
            event_type=NetworkEvent.EventType.LATENCY_SPIKE,
            severity=NetworkEvent.Severity.WARNING,
            message=f'Latency spike on {device.name}: {data["latency_ms"]:.0f}ms',
            detail={'latency_ms': data['latency_ms']},
        )

    _push_ws_update({
        'id': device.id, 'name': device.name, 'status': device.status,
        'latency_ms': data['latency_ms'], 'packet_loss_pct': data['packet_loss_pct'],
        'region': device.region.name if device.region else None,
        'polled_at': poll.polled_at.isoformat(),
    })
    return {'device': device.name, 'status': device.status}


@shared_task
def poll_all_devices():
    ids = list(Device.objects.filter(is_active=True).values_list('id', flat=True))
    for did in ids:
        poll_single_device.delay(did)
    return f'Dispatched polls for {len(ids)} devices'


@shared_task
def evaluate_faults():
    from alerts.notifier import notify_fault
    faults = NetworkEvent.objects.filter(resolved=False, severity__in=['critical','warning']).select_related('device')
    notified = sum(1 for e in faults if notify_fault(e))
    return f'Notified {notified} fault(s)'


@shared_task
def cleanup_old_events():
    from datetime import timedelta
    c_polls  = timezone.now() - timedelta(days=7)
    c_events = timezone.now() - timedelta(days=90)
    dp, _ = PollResult.objects.filter(polled_at__lt=c_polls).delete()
    de, _ = NetworkEvent.objects.filter(occurred_at__lt=c_events, resolved=True).delete()
    return f'Cleaned {dp} polls, {de} events'
