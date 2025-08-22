import pyshark
from pyshark.packet.packet import Packet

DEFAULT_INTERFACE = "eth0"


def packet_summary(pkt: Packet):
    # Timestamp
    ts = pkt.sniff_time.isoformat()


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
