from django.db import models
from django.utils import timezone


class Region(models.Model):
    name      = models.CharField(max_length=100, unique=True)
    code      = models.CharField(max_length=10, unique=True)
    latitude  = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.name


class Device(models.Model):
    class DeviceType(models.TextChoices):
        ROUTER       = 'router',      'Router'
        SWITCH       = 'switch',      'Switch'
        BASE_STATION = 'basestation', 'Base Station'
        FIREWALL     = 'firewall',    'Firewall'
        SERVER       = 'server',      'Server'

    class Status(models.TextChoices):
        UP       = 'up',      'Up'
        DOWN     = 'down',    'Down'
        DEGRADED = 'warn',    'Degraded'
        UNKNOWN  = 'unknown', 'Unknown'

    name           = models.CharField(max_length=100, unique=True)
    ip_address     = models.GenericIPAddressField(unique=True)
    device_type    = models.CharField(max_length=20, choices=DeviceType.choices)
    region         = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, related_name='devices')
    snmp_community = models.CharField(max_length=100, default='public')
    snmp_port      = models.PositiveIntegerField(default=161)
    snmp_version   = models.CharField(max_length=5, default='2c')
    status         = models.CharField(max_length=10, choices=Status.choices, default=Status.UNKNOWN)
    last_seen      = models.DateTimeField(null=True, blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)
    is_active      = models.BooleanField(default=True)
    notes          = models.TextField(blank=True)

    class Meta:
        ordering = ['region__name', 'name']

    def __str__(self):
        return f'{self.name} ({self.ip_address})'

    def mark_up(self):
        self.status = self.Status.UP
        self.last_seen = timezone.now()
        self.save(update_fields=['status', 'last_seen'])

    def mark_down(self):
        self.status = self.Status.DOWN
        self.save(update_fields=['status'])

    def mark_degraded(self):
        self.status = self.Status.DEGRADED
        self.last_seen = timezone.now()
        self.save(update_fields=['status', 'last_seen'])


class Interface(models.Model):
    device       = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='interfaces')
    name         = models.CharField(max_length=50)
    description  = models.CharField(max_length=200, blank=True)
    speed_mbps   = models.PositiveIntegerField(null=True, blank=True)
    is_up        = models.BooleanField(default=True)
    last_in_bps  = models.BigIntegerField(default=0)
    last_out_bps = models.BigIntegerField(default=0)

    def __str__(self):
        return f'{self.device.name} — {self.name}'
