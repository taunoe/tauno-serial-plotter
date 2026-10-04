"""Unit tests for the serial plot data model."""

import unittest

from src.app_model import PlotBuffer


class PlotBufferTests(unittest.TestCase):
    def test_starts_with_single_time_point_and_no_series(self):
        buffer = PlotBuffer(data_size=400)

        self.assertEqual(buffer.number_of_lines, 0)
        self.assertEqual(buffer.x_axis, [0])
        self.assertEqual(buffer.y_axis, [])

    def test_configure_creates_independent_series(self):
        buffer = PlotBuffer(data_size=10)

        buffer.configure(2)

        self.assertEqual(buffer.number_of_lines, 2)
        self.assertEqual(buffer.x_axis, [0])
        self.assertEqual(buffer.y_axis, [[0], [0]])
        self.assertIsNot(buffer.y_axis[0], buffer.y_axis[1])

    def test_add_numbers_converts_values_and_ignores_extra_series(self):
        buffer = PlotBuffer(data_size=10)
        buffer.configure(2)

        buffer.add_numbers(["1.5", 2, 99])

        self.assertEqual(buffer.y_axis, [[0, 1.5], [0, 2.0]])

    def test_add_time_keeps_axes_equal(self):
        buffer = PlotBuffer(data_size=10)
        buffer.configure(2)

        buffer.add_numbers([1, 2])
        buffer.add_time()

        self.assertEqual(buffer.x_axis, [0, 1])
        self.assertEqual(buffer.y_axis, [[0, 1.0], [0, 2.0]])

    def test_buffer_does_not_grow_beyond_data_size_plus_initial_point(self):
        buffer = PlotBuffer(data_size=3)
        buffer.configure(1)

        for value in range(5):
            buffer.add_numbers([value])
            buffer.add_time()

        self.assertEqual(len(buffer.x_axis), 4)
        self.assertEqual(len(buffer.y_axis[0]), 4)
        self.assertEqual(buffer.x_axis, [2, 3, 4, 5])
        self.assertEqual(buffer.y_axis[0], [1.0, 2.0, 3.0, 4.0])

    def test_resize_smaller_trims_oldest_points(self):
        buffer = PlotBuffer(data_size=10)
        buffer.configure(1)
        for value in range(5):
            buffer.add_numbers([value])
            buffer.add_time()

        buffer.resize(2)

        self.assertEqual(buffer.data_size, 2)
        self.assertEqual(buffer.x_axis, [4, 5])
        self.assertEqual(buffer.y_axis[0], [3.0, 4.0])

    def test_resize_larger_preserves_existing_points(self):
        buffer = PlotBuffer(data_size=2)
        buffer.configure(1)
        buffer.add_numbers([7])
        buffer.add_time()

        buffer.resize(10)

        self.assertEqual(buffer.x_axis, [0, 1])
        self.assertEqual(buffer.y_axis[0], [0, 7.0])

    def test_equalize_trims_longer_axis(self):
        buffer = PlotBuffer(data_size=10)
        buffer.configure(1)
        buffer.x_axis = [0, 1, 2]
        buffer.y_axis[0] = [10, 20]

        buffer.equalize()

        self.assertEqual(buffer.x_axis, [1, 2])
        self.assertEqual(buffer.y_axis[0], [10, 20])

    def test_clear_preserves_one_point(self):
        buffer = PlotBuffer(data_size=10)
        buffer.configure(1)
        buffer.add_numbers([1])
        buffer.add_time()
        buffer.add_numbers([2])
        buffer.add_time()

        buffer.clear()

        self.assertEqual(buffer.x_axis, [2])
        self.assertEqual(buffer.y_axis[0], [2.0])


if __name__ == "__main__":
    unittest.main()
