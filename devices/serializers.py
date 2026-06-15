from rest_framework import serializers
from .models import Device, Region, Interface


class RegionSerializer(serializers.ModelSerializer):
    device_count = serializers.SerializerMethodField()
    class Meta:
        model = Region
        fields = '__all__'
    def get_device_count(self, obj):
        return obj.devices.count()


class InterfaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interface
        fields = '__all__'


class DeviceSerializer(serializers.ModelSerializer):
    region_name = serializers.CharField(source='region.name', read_only=True)
    interfaces  = InterfaceSerializer(many=True, read_only=True)
    class Meta:
        model = Device
        fields = '__all__'


class DeviceStatusSerializer(serializers.ModelSerializer):
    """Lightweight — used for WebSocket pushes."""
    region_name = serializers.CharField(source='region.name', read_only=True)
    class Meta:
        model = Device
        fields = ['id', 'name', 'ip_address', 'device_type', 'status', 'region_name', 'last_seen']
