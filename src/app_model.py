"""Application state and serial plot data model."""
from dataclasses import dataclass, field
from enum import Enum, auto
import logging
from typing import Iterable, List, Optional

from PyQt6.QtCore import QSettings


class ConnectionState(Enum):
    """States in the serial connection lifecycle."""
    DISCONNECTED = auto()
    CONNECTING = auto()
    CONNECTED = auto()
    ERROR = auto()


@dataclass
class SerialSettings:
    """Persisted and currently selected serial connection settings."""
    port: str
    baudrate: str


@dataclass
class PlotBuffer:
    """The bounded time series used by the plot."""
    data_size: int
    number_of_lines: int = 0
    x_axis: List[float] = field(default_factory=lambda: [0])
    y_axis: List[List[float]] = field(default_factory=list)

    def configure(self, number_of_lines: int) -> None:
        self.number_of_lines = number_of_lines
        self.x_axis = [0]
        self.y_axis = [[0] for _ in range(number_of_lines)]

    def add_numbers(self, values: Iterable[float]) -> None:
        for i, value in enumerate(values[:self.number_of_lines]):
            if len(self.y_axis[i]) > self.data_size:
                self.y_axis[i] = self.y_axis[i][1:]
            self.y_axis[i].append(float(value))

    def add_time(self) -> None:
        if len(self.x_axis) > self.data_size:
            self.x_axis = self.x_axis[1:]
        self.x_axis.append(self.x_axis[-1] + 1)
        self.equalize()

    def equalize(self) -> None:
        for values in self.y_axis:
            if len(self.x_axis) > len(values):
                del self.x_axis[:len(self.x_axis) - len(values)]
            elif len(values) > len(self.x_axis):
                del values[:len(values) - len(self.x_axis)]

    def resize(self, data_size: int) -> None:
        old_size = self.data_size
        self.data_size = data_size
        if data_size < old_size and self.x_axis:
            difference = len(self.x_axis) - data_size
            if difference > 1:
                del self.x_axis[:difference]
                for values in self.y_axis:
                    del values[:difference]

    def clear(self) -> None:
        size = len(self.x_axis)
        del self.x_axis[:max(size - 1, 0)]
        for values in self.y_axis:
            del values[:max(size - 1, 0)]


class AppModel:
    """Own non-visual application state and serial/plot data operations."""
    BAUDRATES = [
        '150', '200', '300', '600', '1200', '1800', '2400', '4800',
        '9600', '19200', '28800', '38400', '57600', '74880', '76800',
        '115200', '230400', '250000', '460800', '500000', '576000'
    ]
    DEFAULT_BAUD_INDEX = 8

    def __init__(self, settings: Optional[QSettings] = None, data_size: int = 400):
        self.settings = settings or QSettings("TaunoErik", "TaunoSerialPlotter")
        baudrate = self.settings.value(
            "serial/baudrate", self.BAUDRATES[self.DEFAULT_BAUD_INDEX], type=str)
        if baudrate not in self.BAUDRATES:
            baudrate = self.BAUDRATES[self.DEFAULT_BAUD_INDEX]
        self.serial = SerialSettings(
            self.settings.value("serial/port", "", type=str), baudrate)
        self.ports = ['']
        self.labels = ["label"]
        self.connection_state = ConnectionState.DISCONNECTED
        self.plot = PlotBuffer(data_size)
        self.error_counter = 0

    @property
    def selected_port(self) -> str:
        return self.serial.port

    @selected_port.setter
    def selected_port(self, value: str) -> None:
        self.serial.port = value
        self.settings.setValue("serial/port", value)

    @property
    def selected_baudrate(self) -> str:
        return self.serial.baudrate

    @selected_baudrate.setter
    def selected_baudrate(self, value: str) -> None:
        self.serial.baudrate = value
        self.settings.setValue("serial/baudrate", value)

    def set_connection_state(self, state: ConnectionState) -> bool:
        valid = {
            ConnectionState.DISCONNECTED: {ConnectionState.CONNECTING, ConnectionState.ERROR},
            ConnectionState.CONNECTING: {ConnectionState.CONNECTED, ConnectionState.DISCONNECTED,
                                         ConnectionState.ERROR},
            ConnectionState.CONNECTED: {ConnectionState.CONNECTING, ConnectionState.DISCONNECTED,
                                        ConnectionState.ERROR},
            ConnectionState.ERROR: {ConnectionState.CONNECTING, ConnectionState.DISCONNECTED},
        }
        if state != self.connection_state and state not in valid[self.connection_state]:
            logging.warning("Ignoring invalid connection transition: %s -> %s",
                            self.connection_state.name, state.name)
            return False
        self.connection_state = state
        return True

    def configure_plot(self, number_of_lines: int, labels: Optional[List[str]]) -> None:
        self.labels = labels or ["label"]
        self.plot.configure(number_of_lines)

    def add_data(self, values: Iterable[float]) -> None:
        self.plot.add_numbers(values)
        self.plot.add_time()

    def update_data_size(self, value: int) -> None:
        self.plot.resize(value)

    def clear_data(self) -> None:
        self.plot.clear()

    def save_settings(self) -> None:
        self.settings.sync()
