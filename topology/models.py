from django.db import models
from devices.models import Device


class TopologyLink(models.Model):
    parent         = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='child_links')
    child          = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='parent_links')
    link_type      = models.CharField(max_length=30, default='ethernet')
    bandwidth_mbps = models.PositiveIntegerField(null=True, blank=True)
    is_active      = models.BooleanField(default=True)

    class Meta:
        unique_together = [('parent', 'child')]

    def __str__(self):
        return f'{self.parent.name} -> {self.child.name}'
