from rest_framework.decorators import api_view
from rest_framework.response import Response
from devices.models import Device
from .models import TopologyLink


@api_view(['GET'])
def topology_graph(request):
    devices = Device.objects.filter(is_active=True).select_related('region')
    links   = TopologyLink.objects.filter(is_active=True).select_related('parent', 'child')
    return Response({
        'nodes': [{'id': d.id, 'label': d.name, 'type': d.device_type,
                   'status': d.status, 'region': d.region.name if d.region else None,
                   'ip': d.ip_address} for d in devices],
        'edges': [{'source': l.parent_id, 'target': l.child_id,
                   'type': l.link_type, 'bw': l.bandwidth_mbps} for l in links],
    })
