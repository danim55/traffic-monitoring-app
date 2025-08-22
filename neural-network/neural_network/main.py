import pyshark
from pyshark.packet.fields import LayerFieldsContainer
from pyshark.packet.packet import Packet

DEFAULT_INTERFACE = "eth0"


def safe_get(layer, attr, default=None) -> LayerFieldsContainer:
    try:
        return getattr(layer, attr)
    except Exception:
        return default


def packet_summary(pkt: Packet):
    # Timestamp
    timestamp = pkt.sniff_time.isoformat()

    # IP version + addresses
    if hasattr(pkt, 'ip'):
        ip_ver = 'IPv4'
        src = safe_get(pkt.ip, 'src')
        dst = safe_get(pkt.ip, 'dst')
        proto_num = safe_get(pkt.ip, 'proto')  # numeric
    elif hasattr(pkt, 'ipv6'):
        ip_ver = 'IPv6'
        src = safe_get(pkt.ipv6, 'src')
        dst = safe_get(pkt.ipv6, 'dst')
        proto_num = safe_get(pkt.ipv6, 'nxt')  # next header
    else:
        ip_ver = 'Non-IP'
        src = dst = proto_num = None

    # Transport info (TCP/UDP if present)
    transport_prot = pkt.transport_layer
    source_port = dest_port = None
    flags = None
    if transport_prot == 'TCP' and hasattr(pkt, 'tcp'):
        source_port = safe_get(pkt.tcp, 'srcport')
        dest_port = safe_get(pkt.tcp, 'dstport')
        flags = safe_get(pkt.tcp, 'flags')  # raw flags string
    elif transport_prot == 'UDP' and hasattr(pkt, 'udp'):
        source_port = safe_get(pkt.udp, 'srcport')
        dest_port = safe_get(pkt.udp, 'dstport')

    # Frame length (falls back to frame_info)
    length = None
    try:
        length = int(getattr(pkt, 'length', getattr(pkt.frame_info, 'len')))
    except Exception:
        pass

    # Compose a preview line
    parts = [
        timestamp, ip_ver or '',
        f"{src}:{source_port}" if src else '',
        "->",
        f"{dst}:{dest_port}" if dst else '',
                   transport_prot or '',
        f"len={length}" if length else '',
        f"flags={flags}" if flags else '',
        f"highest={pkt.highest_layer}"
    ]
    return " ".join(p for p in parts if p)


def sniff(interface=DEFAULT_INTERFACE, bpf_filter=None):
    print(f"Sniffing on {interface} ... (Ctrl-C to stop)")
    capture = pyshark.LiveCapture(interface=interface, bpf_filter=bpf_filter)
    for pkt in capture.sniff_continuously():
        try:
            print(packet_summary(pkt))
        except KeyboardInterrupt:
            raise
        except Exception as e:
            # Keep running even if some packet lacks fields we expect
            print(f"[warn] skipped packet: {e}")


if __name__ == "__main__":
    sniff(interface=DEFAULT_INTERFACE, bpf_filter="ip or ip6")
