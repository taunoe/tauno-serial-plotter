"""Unit tests for serial-port discovery helpers."""

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from PyQt6.QtWidgets import QApplication

from src.serial_workers import PortScanner, include_serial_port


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


if __name__ == "__main__":
    unittest.main()
