"""Offscreen widget tests for the plotter controls and plot."""

import unittest
from unittest.mock import patch

from PyQt6.QtWidgets import QApplication

from src.theme import create_theme
from src.widgets import Controls, Plot


class WidgetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.application = QApplication.instance() or QApplication([])
        cls.theme = create_theme(cls.application)

    def test_controls_create_expected_widgets(self):
        controls = Controls(theme=self.theme)

        self.assertEqual(controls.select_baud.count(), 0)
        self.assertEqual(controls.select_baud.currentText(), "")
        self.assertEqual(controls.select_port.count(), 0)
        self.assertEqual(controls.connect.text(), "Connect")
        self.assertEqual(
            [controls.select_graph_type.itemData(i)
             for i in range(controls.select_graph_type.count())],
            ["line", "scatter", "bar"],
        )
        self.assertEqual(controls.select_graph_type.currentData(), "line")
        self.assertEqual(controls.time_scale_spin.value(), 400)
        self.assertFalse(controls.btn_clear.isEnabled())
        self.assertFalse(controls.about.icon().isNull())

    def test_controls_have_expected_dimensions_and_styles(self):
        controls = Controls(theme=self.theme)

        self.assertEqual(controls.select_baud.width(), 100)
        self.assertEqual(controls.select_port.width(), 150)
        self.assertEqual(controls.connect.width(), 100)
        self.assertIn(self.theme.colors["gray"], controls.select_baud.styleSheet())
        self.assertIn(self.theme.colors["gray"], controls.select_port.styleSheet())
        self.assertIn(self.theme.colors["orange"], controls.connect.styleSheet())

    def test_update_timescale_updates_control_state(self):
        controls = Controls(theme=self.theme)

        controls.update_timescale(750)

        self.assertEqual(controls.plot_timescale, 750)

    def test_plot_creates_data_series_and_labels(self):
        plot = Plot(2, ["temperature", "humidity"], theme=self.theme)

        self.assertEqual(plot.nr_plot_lines, 2)
        self.assertEqual(plot.data_labels, ["temperature", "humidity"])
        self.assertEqual(plot.x_axis, [0])
        self.assertEqual(plot.y_axis, [[0], [0]])
        self.assertEqual(len(plot.data_lines), 2)

    def test_plot_supports_unlabeled_series(self):
        plot = Plot(1, ["label"], theme=self.theme)

        self.assertEqual(len(plot.data_lines), 1)
        self.assertEqual(plot.data_lines[0].name(), "label")

    def test_plot_background_matches_light_theme(self):
        with patch("src.theme._system_theme", return_value="light"), \
                patch("src.theme._system_accent_color", return_value="#123456"):
            theme = create_theme(self.application)

        plot = Plot(1, ["value"], theme=theme)

        self.assertEqual(
            plot.backgroundBrush().color().name().lower(),
            theme.colors["dark"].lower(),
        )

    def test_plot_switches_graph_type_without_losing_data(self):
        plot = Plot(2, ["temperature", "humidity"], theme=self.theme)
        x_axis = [0, 1]
        y_axis = [[0, 21.5], [0, 50.0]]

        plot.set_data(x_axis, y_axis)
        plot.set_graph_type("scatter")

        self.assertEqual(plot.graph_type, "scatter")
        self.assertEqual(plot.x_axis, x_axis)
        self.assertEqual(plot.y_axis, y_axis)
        self.assertEqual(len(plot.data_lines), 2)
        self.assertEqual(list(plot.data_lines[0].getData()[1]), y_axis[0])

        plot.set_graph_type("bar")
        self.assertEqual(plot.graph_type, "bar")
        self.assertEqual(len(plot.data_lines), 2)
        self.assertEqual(
            [bar.opts["height"][0] for bar in plot.data_lines],
            [21.5, 50.0],
        )

        plot.set_data([0, 1, 2], [[0, 21.5, -3], [0, 50.0, 9]])
        self.assertEqual(
            [bar.opts["height"][0] for bar in plot.data_lines],
            [-3, 9],
        )
        self.assertEqual(
            plot.serialplot.getAxis("bottom")._tickLevels[0],
            [(0, "temperature"), (1, "humidity")],
        )

        with self.assertRaises(ValueError):
            plot.set_graph_type("invalid")


if __name__ == "__main__":
    unittest.main()
