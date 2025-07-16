import pyshark


def dummy_test_aux(value: int) -> int:
    return value


def capture_traffic() -> None:
    capture = pyshark.LiveCapture(interface="eth0")
    capture.sniff_continuously()

    for pkt in capture:
        print(len(pkt))


if __name__ == "__main__":
    capture_traffic()
