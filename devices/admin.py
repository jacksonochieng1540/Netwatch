from django.contrib import admin
from .models import Device, Region, Interface

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'latitude', 'longitude']

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display  = ['name', 'ip_address', 'device_type', 'region', 'status', 'last_seen', 'is_active']
    list_filter   = ['status', 'device_type', 'region', 'is_active']
    search_fields = ['name', 'ip_address']
    list_editable = ['is_active']

@admin.register(Interface)
class InterfaceAdmin(admin.ModelAdmin):
    list_display = ['device', 'name', 'description', 'speed_mbps', 'is_up']
