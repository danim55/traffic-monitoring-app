from datetime import datetime

import pyshark

def dummy_test(value: int) -> int:
    return value


def test_pyshark() -> None:
    capture = pyshark.LiveCapture(interface="eth0")

    for pkt in capture.sniff_continuously():
        ts = datetime.fromtimestamp(float(pkt.sniff_timestamp))
        print(pkt)
        print(ts)


if __name__ == "__main__":
    test_pyshark()
