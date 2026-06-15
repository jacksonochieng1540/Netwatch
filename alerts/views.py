from rest_framework import viewsets, serializers as s
from .models import AlertRule, AlertRecord


class AlertRuleSerializer(s.ModelSerializer):
    class Meta:
        model = AlertRule
        fields = '__all__'


class AlertRecordSerializer(s.ModelSerializer):
    class Meta:
        model = AlertRecord
        fields = '__all__'


class AlertRuleViewSet(viewsets.ModelViewSet):
    queryset = AlertRule.objects.all()
    serializer_class = AlertRuleSerializer


class AlertRecordViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AlertRecord.objects.select_related('event','event__device').order_by('-sent_at')[:200]
    serializer_class = AlertRecordSerializer
