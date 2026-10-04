"""Unit tests for serial-line parsing helpers."""

import unittest

from src.parser import parse_labels, parse_numbers


class ParseNumbersTests(unittest.TestCase):
    def test_parses_signed_integers_and_decimals(self):
        self.assertEqual(
            parse_numbers("1 -2 +3.0 0.25 -.5"),
            ["1", "-2", "+3.0", "0.25", "-.5"],
        )

    def test_parses_values_from_labeled_input(self):
        self.assertEqual(
            parse_numbers("temperature: 21.5, humidity: -3"),
            ["21.5", "-3"],
        )

    def test_returns_empty_list_without_numbers(self):
        self.assertEqual(parse_numbers("temperature: ready"), [])
        self.assertEqual(parse_numbers(""), [])
        self.assertEqual(parse_numbers("   "), [])


class ParseLabelsTests(unittest.TestCase):
    def test_parses_alphabetic_labels(self):
        self.assertEqual(
            parse_labels("temperature: 21.5, humidity: -3"),
            ["temperature", "humidity"],
        )

    def test_parses_signed_and_dotted_labels(self):
        self.assertEqual(
            parse_labels("+temp: 1, sensor.one: 2"),
            ["+temp", "sensor.one"],
        )

    def test_returns_empty_list_without_labels(self):
        self.assertEqual(parse_labels("1 -2.5 +3"), [])
        self.assertEqual(parse_labels(""), [])
        self.assertEqual(parse_labels("123"), [])


if __name__ == "__main__":
    unittest.main()
