from django.db import models
from devices.models import Device


class PollResult(models.Model):
    device          = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='poll_results')
    polled_at       = models.DateTimeField(auto_now_add=True, db_index=True)
    is_reachable    = models.BooleanField(default=False)
    latency_ms      = models.FloatField(null=True, blank=True)
    packet_loss_pct = models.FloatField(null=True, blank=True)
    cpu_util_pct    = models.FloatField(null=True, blank=True)
    mem_util_pct    = models.FloatField(null=True, blank=True)
    uptime_seconds  = models.BigIntegerField(null=True, blank=True)
    raw_snmp        = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-polled_at']
        indexes  = [models.Index(fields=['device', '-polled_at'])]

    def __str__(self):
        return f'{self.device.name} @ {self.polled_at:%Y-%m-%d %H:%M:%S}'


class NetworkEvent(models.Model):
    class EventType(models.TextChoices):
        STATUS_CHANGE = 'status_change', 'Status Change'
        LATENCY_SPIKE = 'latency_spike', 'Latency Spike'
        PACKET_LOSS   = 'packet_loss',   'Packet Loss'
        LINK_DOWN     = 'link_down',     'Link Down'
        SNMP_TIMEOUT  = 'snmp_timeout',  'SNMP Timeout'
        RECOVERY      = 'recovery',      'Recovery'

    class Severity(models.TextChoices):
        INFO     = 'info',     'Info'
        WARNING  = 'warning',  'Warning'
        CRITICAL = 'critical', 'Critical'

    device      = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='events')
    event_type  = models.CharField(max_length=30, choices=EventType.choices)
    severity    = models.CharField(max_length=10, choices=Severity.choices)
    message     = models.TextField()
    detail      = models.JSONField(default=dict, blank=True)
    occurred_at = models.DateTimeField(auto_now_add=True, db_index=True)
    resolved    = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-occurred_at']

    def __str__(self):
        return f'[{self.severity}] {self.device.name}: {self.event_type}'
