"""Unit tests for application state and serial settings."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from PyQt6.QtCore import QSettings

from src.app_model import AppModel, ConnectionState


class AppModelTests(unittest.TestCase):
    def make_settings(self, directory):
        return QSettings(
            str(Path(directory) / "settings.ini"),
            QSettings.Format.IniFormat,
        )

    def test_starts_disconnected_with_default_serial_settings(self):
        with tempfile.TemporaryDirectory() as directory:
            model = AppModel(self.make_settings(directory))

            self.assertEqual(model.connection_state, ConnectionState.DISCONNECTED)
            self.assertEqual(model.selected_port, "")
            self.assertEqual(
                model.selected_baudrate,
                model.BAUDRATES[model.DEFAULT_BAUD_INDEX],
            )

    def test_valid_connection_state_transitions_are_applied(self):
        with tempfile.TemporaryDirectory() as directory:
            model = AppModel(self.make_settings(directory))

            for state in (
                ConnectionState.CONNECTING,
                ConnectionState.CONNECTED,
                ConnectionState.DISCONNECTED,
                ConnectionState.ERROR,
                ConnectionState.CONNECTING,
            ):
                self.assertTrue(model.set_connection_state(state))
                self.assertEqual(model.connection_state, state)

    def test_invalid_connection_state_transition_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            model = AppModel(self.make_settings(directory))

            self.assertFalse(
                model.set_connection_state(ConnectionState.CONNECTED))
            self.assertEqual(
                model.connection_state,
                ConnectionState.DISCONNECTED,
            )

    def test_repeating_current_connection_state_is_allowed(self):
        with tempfile.TemporaryDirectory() as directory:
            model = AppModel(self.make_settings(directory))

            self.assertTrue(
                model.set_connection_state(ConnectionState.DISCONNECTED))
            self.assertEqual(
                model.connection_state,
                ConnectionState.DISCONNECTED,
            )

    def test_invalid_saved_baudrate_falls_back_to_default(self):
        with tempfile.TemporaryDirectory() as directory:
            settings = self.make_settings(directory)
            settings.setValue("serial/baudrate", "not-a-baudrate")
            settings.sync()

            model = AppModel(settings)

            self.assertEqual(
                model.selected_baudrate,
                model.BAUDRATES[model.DEFAULT_BAUD_INDEX],
            )

    def test_port_and_baudrate_changes_are_persisted(self):
        with tempfile.TemporaryDirectory() as directory:
            settings_path = Path(directory) / "settings.ini"
            model = AppModel(self.make_settings(directory))
            model.selected_port = "/dev/ttyUSB0"
            model.selected_baudrate = "115200"
            model.save_settings()

            reloaded = AppModel(
                QSettings(str(settings_path), QSettings.Format.IniFormat))

            self.assertEqual(reloaded.selected_port, "/dev/ttyUSB0")
            self.assertEqual(reloaded.selected_baudrate, "115200")

    def test_save_settings_syncs_qsettings(self):
        with tempfile.TemporaryDirectory() as directory:
            settings = self.make_settings(directory)
            settings.sync = Mock(wraps=settings.sync)
            model = AppModel(settings)

            model.save_settings()

            settings.sync.assert_called_once_with()

    def test_configure_plot_uses_fallback_label(self):
        with tempfile.TemporaryDirectory() as directory:
            model = AppModel(self.make_settings(directory))

            model.configure_plot(1, [])

            self.assertEqual(model.labels, ["label"])
            self.assertEqual(model.plot.number_of_lines, 1)


if __name__ == "__main__":
    unittest.main()
