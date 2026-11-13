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

    def reconnect(self, number_of_lines, labels):
        self.window.model.set_connection_state(ConnectionState.DISCONNECTED)
        self.window.model.set_connection_state(ConnectionState.CONNECTING)
        self.window.serial_connected(number_of_lines, labels)

    def test_reconnect_with_other_series_count_rebuilds_plot(self):
        self.window.model.set_connection_state(ConnectionState.CONNECTING)
        self.window.serial_connected(3, ["a", "b", "c"])
        first_plot = self.window.plot

        self.reconnect(1, ["x"])
        self.assertIs(self.window.plot, first_plot)
        self.assertEqual(len(self.window.plot.data_lines), 1)
        self.assertEqual(self.window.plot.data_lines[0].name(), "x")
        self.window.handle_serial_data("5\n")
        self.window.refresh_plot()
        self.assertEqual(self.window.model.plot.y_axis, [[0, 5.0]])
        self.assertEqual(self.window.plot.y_axis, [[0, 5.0]])
        self.assertEqual(list(self.window.plot.data_lines[0].getData()[1]), [0, 5.0])

        self.reconnect(5, list("abcde"))
        self.assertEqual(len(self.window.plot.data_lines), 5)
        self.assertEqual(
            [item.text for _sample, item in self.window.plot.legend.items],
            list("abcde"),
        )

    def test_reconnect_keeps_selected_graph_type(self):
        self.window.model.set_connection_state(ConnectionState.CONNECTING)
        self.window.serial_connected(2, ["x", "y"])
        self.window.controls.select_graph_type.setCurrentIndex(2)

        self.reconnect(3, ["x", "y", "z"])

        self.assertEqual(self.window.plot.graph_type, "bar")
        self.assertEqual(len(self.window.plot.data_lines), 3)
        self.assertEqual(
            self.window.plot.serialplot.getAxis("bottom")._tickLevels[0],
            [(0, "x"), (1, "y"), (2, "z")],
        )

    def test_incoming_data_updates_plot_buffers(self):
        self.window.model.set_connection_state(ConnectionState.CONNECTING)
        self.window.serial_connected(2, ["x", "y"])

        self.window.handle_serial_data("1.5, 2.5\n")

        self.assertEqual(self.window.model.plot.x_axis, [0, 1])
        self.assertEqual(
            self.window.model.plot.y_axis,
            [[0, 1.5], [0, 2.5]],
        )
        self.assertEqual(self.window.data_sidebar.text_view.toPlainText(), "1.5, 2.5\n")

    def test_many_lines_cause_one_redraw(self):
        self.window.model.set_connection_state(ConnectionState.CONNECTING)
        self.window.serial_connected(2, ["x", "y"])
        self.window.refresh_plot()

        with patch.object(self.window.plot, "set_data",
                          wraps=self.window.plot.set_data) as set_data:
            for value in range(200):
                self.window.handle_serial_data(f"{value}, {value}\n")
            self.assertEqual(set_data.call_count, 0)
            self.assertEqual(len(self.window.model.plot.x_axis), 201)

            self.window.refresh_plot()
            self.window.refresh_plot()
            self.assertEqual(set_data.call_count, 1)

        self.assertEqual(self.window.plot.y_axis[0][-1], 199.0)

    def test_refresh_timer_runs_only_while_connected(self):
        self.assertFalse(self.window.plot_timer.isActive())

        self.window.model.set_connection_state(ConnectionState.CONNECTING)
        self.window.serial_connected(1, ["x"])
        self.assertTrue(self.window.plot_timer.isActive())

        self.window.handle_serial_data("7\n")
        self.window.disconnect_serial()
        self.window.refresh_plot()   # draws the last sample
        self.assertEqual(self.window.plot.y_axis, [[0, 7.0]])
        self.window.refresh_plot()   # nothing left: stops
        self.assertFalse(self.window.plot_timer.isActive())

    def test_data_sidebar_can_be_opened_and_closed(self):
        self.assertTrue(self.window.data_sidebar.isHidden())

        self.window.controls.btn_data_view.setChecked(True)

        self.assertFalse(self.window.data_sidebar.isHidden())
        self.window.data_sidebar.close_button.click()
        self.assertTrue(self.window.data_sidebar.isHidden())
        self.assertFalse(self.window.controls.btn_data_view.isChecked())

    def test_graph_type_changes_keep_live_plot_data(self):
        self.window.model.set_connection_state(ConnectionState.CONNECTING)
        self.window.serial_connected(2, ["x", "y"])
        self.window.handle_serial_data("1.5, 2.5\n")

        self.window.controls.select_graph_type.setCurrentIndex(1)

        self.assertEqual(self.window.plot.graph_type, "scatter")
        self.assertEqual(self.window.plot.x_axis, [0, 1])
        self.assertEqual(self.window.plot.y_axis, [[0, 1.5], [0, 2.5]])

        self.window.handle_serial_data("3.5, 4.5\n")
        self.window.refresh_plot()
        self.assertEqual(self.window.plot.x_axis, [0, 1, 2])
        self.assertEqual(self.window.plot.y_axis, [[0, 1.5, 3.5], [0, 2.5, 4.5]])

        self.window.clear_data()
        self.assertEqual(self.window.plot.x_axis, [2])
        self.assertEqual(self.window.plot.y_axis, [[3.5], [4.5]])

    def test_bar_graph_uses_latest_value_for_each_label(self):
        self.window.model.set_connection_state(ConnectionState.CONNECTING)
        self.window.serial_connected(2, ["x", "y"])
        self.window.controls.select_graph_type.setCurrentIndex(2)

        self.window.handle_serial_data("1.5, -2.5\n")
        self.window.handle_serial_data("3.5, -4.5\n")
        self.window.refresh_plot()

        self.assertEqual(self.window.plot.graph_type, "bar")
        self.assertEqual(
            [bar.opts["height"][0] for bar in self.window.plot.data_lines],
            [3.5, -4.5],
        )
        self.assertEqual(
            self.window.plot.serialplot.getAxis("bottom")._tickLevels[0],
            [(0, "x"), (1, "y")],
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

        self.window.disconnect_serial()

        self.assertEqual(
            self.window.model.connection_state,
            ConnectionState.DISCONNECTED,
        )
        self.assertEqual(self.window.controls.connect.text(), "Connect")
        self.assertTrue(self.window.controls.select_port.isEnabled())
        self.assertTrue(self.window.controls.select_baud.isEnabled())
        self.assertFalse(self.window.controls.btn_clear.isEnabled())

    def test_qobject_connect_api_is_not_shadowed(self):
        self.assertNotIn("disconnect", vars(MainWindow))
        self.assertNotIn("connect", vars(MainWindow))

    def test_connect_updates_ui_without_starting_real_serial_connection(self):
        self.window.model.selected_port = "/dev/ttyUSB0"
        self.window.model.selected_baudrate = "115200"
        with patch.object(self.window, "request_serial_connection") as request:
            self.window.connect_serial()

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
