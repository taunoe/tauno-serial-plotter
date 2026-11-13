"""Unit tests for serial-port discovery helpers."""

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from PyQt6.QtWidgets import QApplication

from src.serial_workers import PortScanner, SerialWorker, include_serial_port


class SerialPortFilteringTests(unittest.TestCase):
    def port(self, **values):
        defaults = {
            "device": "/dev/ttyS1",
            "manufacturer": None,
            "serial_number": None,
            "product": None,
            "interface": None,
            "location": None,
            "vid": None,
            "pid": None,
            "hwid": "",
        }
        defaults.update(values)
        return SimpleNamespace(**defaults)

    def test_hides_metadata_free_legacy_uart(self):
        self.assertFalse(include_serial_port(self.port()))

    def test_keeps_non_legacy_serial_devices(self):
        self.assertTrue(include_serial_port(self.port(device="/dev/ttyUSB0")))
        self.assertTrue(include_serial_port(self.port(device="/dev/ttyACM0")))

    def test_keeps_legacy_uart_with_device_metadata(self):
        for field in ("manufacturer", "serial_number", "product", "interface", "location"):
            with self.subTest(field=field):
                self.assertTrue(include_serial_port(self.port(**{field: "metadata"})))

    def test_keeps_legacy_uart_with_vid_or_pid(self):
        self.assertTrue(include_serial_port(self.port(vid=0x2341)))
        self.assertTrue(include_serial_port(self.port(pid=0x0043)))

    def test_keeps_legacy_uart_with_usb_hardware_id(self):
        self.assertTrue(include_serial_port(self.port(hwid="USB VID:PID=2341:0043")))
        self.assertTrue(include_serial_port(self.port(hwid="usb serial device")))

    def test_handles_missing_port_attributes(self):
        self.assertFalse(include_serial_port(SimpleNamespace(device="/dev/ttyS2")))
        self.assertTrue(include_serial_port(SimpleNamespace(device="/dev/ttyUSB1")))


class PortScannerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.application = QApplication.instance() or QApplication([])

    def port(self, device, **values):
        defaults = {
            "device": device,
            "manufacturer": None,
            "serial_number": None,
            "product": None,
            "interface": None,
            "location": None,
            "vid": None,
            "pid": None,
            "hwid": "",
        }
        defaults.update(values)
        return SimpleNamespace(**defaults)

    def test_scan_emits_filtered_device_names(self):
        scanner = PortScanner()
        found = []
        scanner.ports_found.connect(found.append)
        ports = [
            self.port("/dev/ttyS1"),
            self.port("/dev/ttyUSB0"),
            self.port("/dev/ttyS2", manufacturer="Arduino"),
        ]

        with patch("src.serial_workers.serial.tools.list_ports.comports",
                   return_value=ports):
            scanner.scan()

        self.assertEqual(found, [["/dev/ttyUSB0", "/dev/ttyS2"]])

    def test_scan_emits_empty_list_when_port_enumeration_fails(self):
        scanner = PortScanner()
        found = []
        scanner.ports_found.connect(found.append)

        with patch(
            "src.serial_workers.serial.tools.list_ports.comports",
            side_effect=OSError("device enumeration failed"),
        ):
            scanner.scan()

        self.assertEqual(found, [[]])

    def test_start_scans_immediately_and_configures_timer(self):
        scanner = PortScanner(interval=3)
        found = []
        scanner.ports_found.connect(found.append)
        ports = [self.port("/dev/ttyACM0")]

        with patch("src.serial_workers.serial.tools.list_ports.comports",
                   return_value=ports):
            scanner.start()

        self.assertEqual(found, [["/dev/ttyACM0"]])
        self.assertIsNotNone(scanner.timer)
        self.assertEqual(scanner.timer.interval(), 3000)
        scanner.timer.stop()
        scanner.deleteLater()


class SerialWorkerTests(unittest.TestCase):
    class FakeSerial:
        def __init__(self):
            self.buffer = b""
            self.is_open = True

        @property
        def in_waiting(self):
            return len(self.buffer)

        def read(self, size):
            result, self.buffer = self.buffer[:size], self.buffer[size:]
            return result

    def test_waits_for_complete_lines_before_parsing_serial_data(self):
        worker = SerialWorker()
        worker.serial = self.FakeSerial()
        worker.probing = True
        connected = []
        received = []
        worker.connected.connect(lambda count, labels: connected.append((count, labels)))
        worker.data_received.connect(received.append)

        worker.serial.buffer = b"x = 1"
        worker.read_serial()
        self.assertEqual(connected, [])
        self.assertEqual(received, [])

        worker.serial.buffer = b"0, kass = 9, koer = 3\n"
        worker.read_serial()

        self.assertEqual(connected, [(3, ["x", "kass", "koer"])])
        self.assertEqual(received, ["x = 10, kass = 9, koer = 3\n"])

    def make_connected_worker(self):
        worker = SerialWorker()
        fake = self.FakeSerial()
        fake.reset_input_buffer = lambda: None
        fake.close = lambda: None
        with patch("src.serial_workers.serial.Serial", return_value=fake):
            worker.connect_to("/dev/ttyUSB0", 9600)
        connected = []
        received = []
        failed = []
        worker.connected.connect(lambda count, labels: connected.append((count, labels)))
        worker.data_received.connect(received.append)
        worker.connection_failed.connect(failed.append)
        return worker, connected, received, failed

    def test_partial_first_line_does_not_decide_series_count(self):
        worker, connected, received, _failed = self.make_connected_worker()

        # The port was opened in the middle of "1, 2, 3".
        worker.serial.buffer = b", 3\n4, 5, 6\n"
        worker.read_serial()

        self.assertEqual(connected, [(3, [])])
        self.assertEqual(received, ["4, 5, 6\n"])

    def test_stream_without_newlines_is_bounded(self):
        worker, connected, received, _failed = self.make_connected_worker()
        worker.MAX_LINE_BYTES = 100

        for _ in range(10):
            worker.serial.buffer = b"7" * 60
            worker.read_serial()
            self.assertLessEqual(len(worker._serial_buffer), 160)

        # The tail of the oversized run is dropped, then data flows again.
        worker.serial.buffer = b"777\n1, 2\n"
        worker.read_serial()
        self.assertEqual(connected, [(2, [])])
        self.assertEqual(received, ["1, 2\n"])

    def test_probe_times_out_when_only_text_arrives(self):
        worker, connected, _received, failed = self.make_connected_worker()
        worker.probe_limit = 5

        for _ in range(5):
            worker.serial.buffer = b"still booting\n"
            worker.read_serial()

        self.assertEqual(connected, [])
        self.assertEqual(failed, ["No numeric data received"])
        self.assertIsNone(worker.serial)


if __name__ == "__main__":
    unittest.main()
