"""Offscreen integration tests for MainWindow event routing."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import QApplication

from src.app_model import ConnectionState
from src.tauno_serial_plotter import MainWindow
from src.theme import create_theme


class MainWindowIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.application = QApplication.instance() or QApplication([])
        cls.theme = create_theme(cls.application)

    def setUp(self):
        self.settings_directory = tempfile.TemporaryDirectory()
        settings = QSettings(
            str(Path(self.settings_directory.name) / "settings.ini"),
            QSettings.Format.IniFormat,
        )
        self.settings_patch = patch("src.app_model.QSettings", return_value=settings)
        self.settings_patch.start()
        self.window = MainWindow(self.application, theme=self.theme)
        self.application.processEvents()

    def tearDown(self):
        self.window.close()
        self.application.processEvents()
        self.settings_patch.stop()
        self.settings_directory.cleanup()

    def test_initial_ui_and_model_state(self):
        self.assertEqual(
            self.window.model.connection_state,
            ConnectionState.DISCONNECTED,
        )
        self.assertEqual(self.window.controls.select_baud.count(), 21)
        self.assertEqual(self.window.controls.connect.text(), "Connect")
        self.assertFalse(self.window.plot_exist)

    def test_port_updates_populate_selector_and_model(self):
        self.window.update_ports(["/dev/ttyUSB0", "/dev/ttyACM0"])

        self.assertEqual(
            [self.window.controls.select_port.itemText(i) for i in range(2)],
            ["/dev/ttyUSB0", "/dev/ttyACM0"],
        )
        self.assertEqual(self.window.model.selected_port, "/dev/ttyUSB0")

    def test_connection_success_creates_plot_and_updates_controls(self):
        self.window.model.set_connection_state(ConnectionState.CONNECTING)

        self.window.serial_connected(2, ["temperature", "humidity"])

        self.assertEqual(
            self.window.model.connection_state,
            ConnectionState.CONNECTED,
        )
        self.assertTrue(self.window.plot_exist)
        self.assertEqual(len(self.window.plot.data_lines), 2)
        self.assertEqual(self.window.controls.connect.text(), "Pause")
        self.assertTrue(self.window.controls.btn_clear.isEnabled())

    def test_incoming_data_updates_plot_buffers(self):
        self.window.model.set_connection_state(ConnectionState.CONNECTING)
        self.window.serial_connected(2, ["x", "y"])

        self.window.handle_serial_data("1.5, 2.5\n")

        self.assertEqual(self.window.model.plot.x_axis, [0, 1])
        self.assertEqual(
            self.window.model.plot.y_axis,
            [[0, 1.5], [0, 2.5]],
        )

    def test_stale_connection_signal_is_ignored(self):
        self.window.serial_connected(1, ["value"])

        self.assertFalse(self.window.plot_exist)
        self.assertEqual(
            self.window.model.connection_state,
            ConnectionState.DISCONNECTED,
        )

    def test_disconnect_restores_editable_controls(self):
        self.window.model.set_connection_state(ConnectionState.CONNECTING)
        self.window.serial_connected(1, ["value"])

        self.window.disconnect()

        self.assertEqual(
            self.window.model.connection_state,
            ConnectionState.DISCONNECTED,
        )
        self.assertEqual(self.window.controls.connect.text(), "Connect")
        self.assertTrue(self.window.controls.select_port.isEnabled())
        self.assertTrue(self.window.controls.select_baud.isEnabled())
        self.assertFalse(self.window.controls.btn_clear.isEnabled())

    def test_connect_updates_ui_without_starting_real_serial_connection(self):
        self.window.model.selected_port = "/dev/ttyUSB0"
        self.window.model.selected_baudrate = "115200"
        with patch.object(self.window, "request_serial_connection") as request:
            self.window.connect()

        self.assertEqual(
            self.window.model.connection_state,
            ConnectionState.CONNECTING,
        )
        self.assertEqual(self.window.controls.connect.text(), "Connecting...")
        self.assertFalse(self.window.controls.select_port.isEnabled())
        self.assertFalse(self.window.controls.select_baud.isEnabled())
        request.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
