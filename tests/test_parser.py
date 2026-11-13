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

    def test_digits_in_separated_labels_are_not_values(self):
        self.assertEqual(parse_numbers("sensor1: 5, sensor2: 7"), ["5", "7"])
        self.assertEqual(parse_numbers("ADC0=12 ADC1=13"), ["12", "13"])
        self.assertEqual(parse_numbers("temp_1 : -4.5"), ["-4.5"])

    def test_parses_scientific_notation(self):
        self.assertEqual(parse_numbers("1.5e-3 2E4 -3e+2"),
                         ["1.5e-3", "2E4", "-3e+2"])
        self.assertEqual([float(n) for n in parse_numbers("1.5e-3 2E4")],
                         [0.0015, 20000.0])

    def test_parses_glued_arduino_example_format(self):
        line = "First12Second14.4Third-3Min:0, Max:100"
        self.assertEqual(parse_numbers(line), ["12", "14.4", "-3", "0", "100"])

    def test_every_parsed_number_is_a_valid_float(self):
        for text in ("1. .5 +7 -0.0", "a1e5b", "192.168.1.1", "1e", "5e+"):
            for number in parse_numbers(text):
                float(number)


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

    def test_separated_labels_keep_trailing_digits_and_underscores(self):
        self.assertEqual(parse_labels("sensor1: 5, sensor2: 7"),
                         ["sensor1", "sensor2"])
        self.assertEqual(parse_labels("temp_a: 1, temp_b = 2"),
                         ["temp_a", "temp_b"])

    def test_glued_labels_stay_letters_only(self):
        self.assertEqual(
            parse_labels("First12Second14.4Min:0, Max:100"),
            ["First", "Second", "Min", "Max"],
        )

    def test_exponent_is_not_reported_as_a_label(self):
        self.assertEqual(parse_labels("1.5e-3 2E4"), [])

    def test_returns_empty_list_without_labels(self):
        self.assertEqual(parse_labels("1 -2.5 +3"), [])
        self.assertEqual(parse_labels(""), [])
        self.assertEqual(parse_labels("123"), [])


if __name__ == "__main__":
    unittest.main()
