from rest_framework import viewsets, mixins, serializers as s
from .models import PollResult, NetworkEvent


class PollResultSerializer(s.ModelSerializer):
    device_name = s.CharField(source='device.name', read_only=True)
    class Meta:
        model = PollResult
        fields = ['id','device','device_name','polled_at','is_reachable',
                  'latency_ms','packet_loss_pct','cpu_util_pct','mem_util_pct','uptime_seconds']


class NetworkEventSerializer(s.ModelSerializer):
    device_name = s.CharField(source='device.name', read_only=True)
    class Meta:
        model = NetworkEvent
        fields = '__all__'


class PollResultViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = PollResultSerializer
    def get_queryset(self):
        qs = PollResult.objects.select_related('device').order_by('-polled_at')
        did = self.request.query_params.get('device')
        return qs.filter(device_id=did)[:200] if did else qs[:200]


class NetworkEventViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = NetworkEventSerializer
    def get_queryset(self):
        qs = NetworkEvent.objects.select_related('device')
        sev = self.request.query_params.get('severity')
        res = self.request.query_params.get('resolved')
        if sev: qs = qs.filter(severity=sev)
        if res is not None: qs = qs.filter(resolved=res.lower()=='true')
        return qs[:200]
