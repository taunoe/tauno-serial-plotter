"""Qt workers for serial-port discovery and serial data transport."""

import logging
import serial
import serial.tools.list_ports
from PyQt6 import QtCore

from parser import parse_labels, parse_numbers


def include_serial_port(port):
    """Hide metadata-free legacy UARTs while retaining real hardware ports."""
    device = getattr(port, "device", "")
    if not device.startswith("/dev/ttyS"):
        return True

    metadata_fields = (
        "manufacturer",
        "serial_number",
        "product",
        "interface",
        "location",
    )
    if any(getattr(port, field, None) for field in metadata_fields):
        return True
    if getattr(port, "vid", None) is not None or getattr(port, "pid", None) is not None:
        return True
    return "USB" in (getattr(port, "hwid", "") or "").upper()


class PortScanner(QtCore.QObject):
    """Scan serial ports in a worker thread and publish results to the GUI."""

    ports_found = QtCore.pyqtSignal(list)

    def __init__(self, interval=10, parent=None):
        super().__init__(parent)
        self.interval = interval
        self.timer = None

    @QtCore.pyqtSlot()
    def start(self):
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(self.interval * 1000)
        self.timer.timeout.connect(self.scan)
        self.scan()
        self.timer.start()

    @QtCore.pyqtSlot()
    def scan(self):
        ports = []
        try:
            ports = [
                port.device
                for port in serial.tools.list_ports.comports()
                if include_serial_port(port)
            ]
        except OSError:
            logging.exception("Unable to scan serial ports")
        self.ports_found.emit(ports)


class SerialWorker(QtCore.QObject):
    """Own the serial connection and perform all serial I/O off the GUI thread."""

    connected = QtCore.pyqtSignal(int, list)
    data_received = QtCore.pyqtSignal(str)
    connection_failed = QtCore.pyqtSignal(str)
    disconnected = QtCore.pyqtSignal()
    stopped = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.serial = None
        self.timer = None
        self.probing = False
        self.probe_attempts = 0
        self.probe_limit = 7500

    @QtCore.pyqtSlot()
    def start(self):
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(10)
        self.timer.timeout.connect(self.read_serial)
        self.timer.start()

    @QtCore.pyqtSlot(str, int)
    def connect_to(self, port, baudrate):
        self._close_serial()
        try:
            self.serial = serial.Serial(port, baudrate, timeout=0)
            self.serial.reset_input_buffer()
            self.probing = True
            self.probe_attempts = 0
        except (OSError, serial.SerialException) as error:
            self.serial = None
            self.connection_failed.emit(str(error))

    @QtCore.pyqtSlot()
    def disconnect_from_serial(self):
        self._close_serial()
        self.disconnected.emit()

    def _close_serial(self):
        self.probing = False
        if self.serial is not None:
            self.serial.close()
            self.serial = None

    @QtCore.pyqtSlot()
    def read_serial(self):
        if self.serial is None or not self.serial.is_open:
            return

        try:
            if self.serial.in_waiting == 0:
                if self.probing:
                    self.probe_attempts += 1
                    if self.probe_attempts >= self.probe_limit:
                        self.disconnect_from_serial()
                        self.connection_failed.emit("No numeric data received")
                return

            line = self.serial.readline().decode("utf8", errors="replace")
            if not line:
                return

            if self.probing:
                numbers = parse_numbers(line)
                if not numbers:
                    return
                labels = parse_labels(line)
                self.probing = False
                self.connected.emit(len(numbers), labels)
            self.data_received.emit(line)
        except (OSError, serial.SerialException, UnicodeError) as error:
            self.disconnect_from_serial()
            self.connection_failed.emit(str(error))

    @QtCore.pyqtSlot()
    def stop(self):
        if self.timer is not None:
            self.timer.stop()
        self.disconnect_from_serial()
        self.stopped.emit()
