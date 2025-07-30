from datetime import datetime, timedelta, timezone

import pyshark

# CONFIGURATION
IDLE_TIMEOUT = timedelta(seconds=120)
ACTIVE_TIMEOUT = timedelta(seconds=600)
INTERFACE = "eth0"


def dummy_test(value: int) -> int:
    return value


class Flow:
    def __init__(self, package, flow_tuple):
        self.packages = [package]
        self.first_timestamp = self.last_timestamp = datetime.now(timezone.utc)  # timezone-aware
        self.key = flow_tuple

    def add_package(self, package):
        self.packages.append(package)
        self.last_timestamp = datetime.now(timezone.utc)

    def is_idle(self):
        return datetime.now(timezone.utc) - self.last_timestamp > IDLE_TIMEOUT

    def is_active_expired(self):
        return datetime.now(timezone.utc) - self.first_timestamp > ACTIVE_TIMEOUT

    def features(self):
        count = len(self.packages)
        duration = (self.last_timestamp - self.first_timestamp).total_seconds()
        byte_total = sum(int(package.length) for package in self.packages)
        return {"count": count, "duration": duration, "bytes": byte_total}

    def is_finished(self, package: object) -> object:
        flags = getattr(package.tcp, 'flags', "")
        return 'F' in flags or 'R' in flags


def capture_flows():
    capture = pyshark.LiveCapture(interface=INTERFACE)
    flows = {}

    for package in capture.sniff_continuously():
        if not hasattr(package, 'ip') or package.transport_layer not in ('TCP', 'UDP'):
            continue

        transport_layer = package.transport_layer
        layer = getattr(package, transport_layer.lower(), None)
        if layer is None:
            continue

        src_port = getattr(layer, 'srcport', None)
        dst_port = getattr(layer, 'dstport', None)
        if src_port is None or dst_port is None:
            continue

        flow_tuple = (package.ip.src, src_port, package.ip.dst, dst_port, transport_layer)
        reverse_flow_tuple = (flow_tuple[2], flow_tuple[3], flow_tuple[0], flow_tuple[1], flow_tuple[4])

        # Close idle/expired flows first
        to_close = [k for k, f in flows.items()
                    if f.is_idle() or f.is_active_expired()]
        for k in to_close:
            flow = flows.pop(k)
            yield flow.features()

        f = flows.get(flow_tuple) or flows.get(reverse_flow_tuple)
        if f:
            f.add_package(package)
            if f.is_finished(package):
                flows.pop(f.key, None)
                yield f.features()
        else:
            flows[flow_tuple] = Flow(package, flow_tuple)


if __name__ == "__main__":
    for flow_features in capture_flows():
        print("Flow closed:", flow_features)
