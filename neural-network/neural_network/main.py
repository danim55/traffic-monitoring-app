from datetime import datetime, timedelta, timezone

import pyshark

# CONFIGURATION
IDLE_TIMEOUT = timedelta(seconds=120)
ACTIVE_TIMEOUT = timedelta(seconds=600)
INTERFACE = "eth0"


def dummy_test(value: int) -> int:
    return value  # placeholder for your logic


class Flow:
    def __init__(self, first_pkt, tpl):
        self.pkts = [first_pkt]
        self.first_ts = self.last_ts = datetime.now(timezone.utc)  # timezone-aware
        self.key = tpl

    def add(self, pkt):
        ts = datetime.now(timezone.utc)
        self.pkts.append(pkt)
        self.last_ts = ts

    def is_finished(self, pkt):
        flags = getattr(pkt.tcp, 'flags', "")
        return 'F' in flags or 'R' in flags

    def is_idle(self):
        return datetime.now(timezone.utc) - self.last_ts > IDLE_TIMEOUT

    def is_active_expired(self):
        return datetime.now(timezone.utc) - self.first_ts > ACTIVE_TIMEOUT

    def features(self):
        count = len(self.pkts)
        duration = (self.last_ts - self.first_ts).total_seconds()
        byte_total = sum(int(p.length) for p in self.pkts)
        return {"count": count, "duration": duration, "bytes": byte_total}


def capture_flows():
    capture = pyshark.LiveCapture(interface=INTERFACE)
    flows = {}

    for pkt in capture.sniff_continuously():
        if not hasattr(pkt, 'ip') or pkt.transport_layer not in ('TCP', 'UDP'):
            continue

        tl = pkt.transport_layer
        layer = getattr(pkt, tl.lower(), None)
        if layer is None:
            continue

        src_port = getattr(layer, 'srcport', None)
        dst_port = getattr(layer, 'dstport', None)
        if src_port is None or dst_port is None:
            continue

        tpl = (pkt.ip.src, src_port, pkt.ip.dst, dst_port, tl)
        rev_tpl = (tpl[2], tpl[3], tpl[0], tpl[1], tpl[4])

        # Close idle/expired flows first
        to_close = [k for k, f in flows.items()
                    if f.is_idle() or f.is_active_expired()]
        for k in to_close:
            flow = flows.pop(k)
            yield flow.features()

        f = flows.get(tpl) or flows.get(rev_tpl)
        if f:
            f.add(pkt)
            if f.is_finished(pkt):
                flows.pop(f.key, None)
                yield f.features()
        else:
            flows[tpl] = Flow(pkt, tpl)


if __name__ == "__main__":
    for flow_feats in capture_flows():
        print("Flow closed:", flow_feats)
