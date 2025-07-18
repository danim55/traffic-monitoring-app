from datetime import datetime, timedelta

import pyshark

# CONFIGURATION
IDLE_TIMEOUT = timedelta(seconds=120)
ACTIVE_TIMEOUT = timedelta(seconds=600)  # optional
INTERFACE = "eth0"


def dummy_test(value: int) -> int:
    return value


class Flow:
    def __init__(self, first_pkt):
        self.pkts = [first_pkt]
        self.first_ts = last_ts = datetime.fromtimestamp(float(first_pkt.sniff_timestamp))
        self.last_ts = last_ts
        self.key = (first_pkt.ip.src, first_pkt[first_pkt.transport_layer].srcport,
                    first_pkt.ip.dst, first_pkt[first_pkt.transport_layer].dstport,
                    first_pkt.transport_layer)

    def add(self, pkt):
        ts = datetime.fromtimestamp(float(pkt.sniff_timestamp))
        self.pkts.append(pkt)
        self.last_ts = ts

    def is_finished(self, pkt):
        flags = pkt.tcp.flags if hasattr(pkt, 'tcp') else ""
        return 'F' in flags or 'R' in flags

    def is_idle(self):
        return datetime.utcnow() - self.last_ts > IDLE_TIMEOUT

    def is_active_expired(self):
        return datetime.utcnow() - self.first_ts > ACTIVE_TIMEOUT

    def features(self):
        # Example: return count, duration, byte_total
        count = len(self.pkts)
        duration = (self.last_ts - self.first_ts).total_seconds()
        byte_total = sum(int(p.length) for p in self.pkts)
        return {"count": count, "duration": duration, "bytes": byte_total}


def capture_flows():
    capture = pyshark.LiveCapture(interface=INTERFACE)
    flows = {}

    for pkt in capture.sniff_continuously():
        if not hasattr(pkt, "ip"):
            continue  # skip non-IP

        captured_tuple = (pkt.ip.src, pkt[pkt.transport_layer].srcport,
               pkt.ip.dst, pkt[pkt.transport_layer].dstport,
               pkt.transport_layer)
        reverse_tuple = (captured_tuple[2], captured_tuple[3], captured_tuple[0], captured_tuple[1], captured_tuple[4])  # reverse captured_tuple

        f = flows.get(captured_tuple) or flows.get(reverse_tuple)
        now = datetime.utcnow()

        # close any idle/expired flows
        to_close = []
        for key, flow in list(flows.items()):
            if flow.is_idle() or flow.is_active_expired():
                to_close.append(key)
        for key in to_close:
            flow = flows.pop(key)
            yield flow.features()

        # New or existing
        if f:
            f.add(pkt)
            # close on FIN/RST
            if f.is_finished(pkt):
                flows.pop(f.key, None)
                yield f.features()
        else:
            f = Flow(pkt)
            flows[f.key] = f


# Example usage
if __name__ == "__main__":
    for flow_feats in capture_flows():
        print("Flow closed:", flow_feats)
