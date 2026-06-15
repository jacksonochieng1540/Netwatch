from django.db import models
from monitoring.models import NetworkEvent


class AlertRule(models.Model):
    name              = models.CharField(max_length=100)
    event_type        = models.CharField(max_length=30, blank=True)
    severity          = models.CharField(max_length=10, blank=True)
    latency_threshold = models.FloatField(null=True, blank=True)
    loss_threshold    = models.FloatField(null=True, blank=True)
    notify_email      = models.BooleanField(default=True)
    notify_sms        = models.BooleanField(default=False)
    is_active         = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class AlertRecord(models.Model):
    event   = models.ForeignKey(NetworkEvent, on_delete=models.CASCADE, related_name='notifications')
    channel = models.CharField(max_length=20)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=['event', 'sent_at'])]
