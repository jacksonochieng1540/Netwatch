from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count
from .models import Device, Region
from .serializers import DeviceSerializer, RegionSerializer, DeviceStatusSerializer


class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.select_related('region').prefetch_related('interfaces').all()
    serializer_class = DeviceSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        for param, field in [('status','status'), ('region','region__code'), ('type','device_type')]:
            val = self.request.query_params.get(param)
            if val:
                qs = qs.filter(**{field: val})
        return qs

    @action(detail=False, methods=['get'])
    def summary(self, request):
        qs = Device.objects.filter(is_active=True)
        return Response({
            'total':    qs.count(),
            'up':       qs.filter(status='up').count(),
            'down':     qs.filter(status='down').count(),
            'degraded': qs.filter(status='warn').count(),
            'unknown':  qs.filter(status='unknown').count(),
        })

    @action(detail=False, methods=['get'], url_path='live-status')
    def live_status(self, request):
        qs = Device.objects.filter(is_active=True).select_related('region')
        return Response(DeviceStatusSerializer(qs, many=True).data)


class RegionViewSet(viewsets.ModelViewSet):
    queryset = Region.objects.annotate(device_count=Count('devices')).all()
    serializer_class = RegionSerializer
