"""
Polling engine — ICMP ping + SNMP, with a simulated fallback for development.
"""
import logging, time
logger = logging.getLogger(__name__)

OIDS = {
    'sysUpTime': '1.3.6.1.2.1.1.3.0',
    'sysDescr':  '1.3.6.1.2.1.1.1.0',
    'cpuLoad':   '1.3.6.1.4.1.9.2.1.58.0',
    'memFree':   '1.3.6.1.4.1.9.2.1.8.0',
}


def ping_device(ip: str, count: int = 5, timeout: float = 2.0) -> dict:
    try:
        from ping3 import ping
        results = [ping(ip, timeout=timeout, unit='ms') for _ in range(count)]
        time.sleep(0.1)
        valid = [r for r in results if r is not None and r is not False]
        if not valid:
            return {'reachable': False, 'latency_ms': None, 'packet_loss_pct': 100.0}
        return {
            'reachable': True,
            'latency_ms': round(sum(valid) / len(valid), 2),
            'packet_loss_pct': round((1 - len(valid) / count) * 100, 2),
        }
    except ImportError:
        import random
        if random.random() < 0.05:
            return {'reachable': False, 'latency_ms': None, 'packet_loss_pct': 100.0}
        return {'reachable': True, 'latency_ms': round(random.uniform(5, 80), 2),
                'packet_loss_pct': round(random.uniform(0, 2), 2)}
    except Exception as exc:
        logger.error('ping_device %s: %s', ip, exc)
        return {'reachable': False, 'latency_ms': None, 'packet_loss_pct': 100.0}


def snmp_get(ip: str, community: str, port: int = 161, version: str = '2c') -> dict:
    try:
        from easysnmp import Session
        session = Session(hostname=ip, community=community, version=2,
                          remote_port=port, timeout=3, retries=1)
        return {name: session.get(oid).value for name, oid in OIDS.items()}
    except ImportError:
        import random
        return {'sysUpTime': str(random.randint(100000, 9999999)),
                'cpuLoad': str(round(random.uniform(5, 60), 1)),
                'memFree': str(random.randint(102400, 1048576))}
    except Exception as exc:
        logger.warning('SNMP %s: %s', ip, exc)
        return {}


def poll_device(device) -> dict:
    ping_data = ping_device(device.ip_address)
    snmp_data = snmp_get(device.ip_address, device.snmp_community,
                         device.snmp_port, device.snmp_version) if ping_data['reachable'] else {}
    cpu = mem = uptime = None
    try:
        cpu    = float(snmp_data.get('cpuLoad') or 0) or None
        mf     = float(snmp_data.get('memFree') or 0)
        mem    = round(100 - (mf / 1048576) * 100, 1) if mf else None
        uptime = int(snmp_data.get('sysUpTime') or 0) // 100 or None
    except (TypeError, ValueError, ZeroDivisionError):
        pass
    return {
        'is_reachable':    ping_data['reachable'],
        'latency_ms':      ping_data['latency_ms'],
        'packet_loss_pct': ping_data['packet_loss_pct'],
        'cpu_util_pct':    cpu,
        'mem_util_pct':    mem,
        'uptime_seconds':  uptime,
        'raw_snmp':        snmp_data,
    }
