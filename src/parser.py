"""Parsing helpers for serial plotter input.

Two line styles are understood and may be mixed on one line:

* Glued labels, as in the Arduino examples: ``First12Second3.5``.
  Here a label is letters only, because a digit starts the value.
* Separated labels: ``sensor1: 12, temp_a = 3.5``.
  A ``:`` or ``=`` ends the label, so it may end in digits.

Values may be integers, decimals or scientific notation (``1.5e-3``).
"""

import re


_NUMBER = r"[-+]?(?:[0-9]+\.?[0-9]*|\.[0-9]+)(?:[eE][-+]?[0-9]+)?"
_WORD = r"[-+]?[A-Za-z_]+(?:\.[A-Za-z_]+)*"

TOKEN_PATTERN = re.compile(
    # A label closed by ':' or '=' may carry trailing digits (sensor1:, ADC0=).
    rf"(?P<key>{_WORD}[0-9]*)\s*[:=]"
    rf"|(?P<number>{_NUMBER})"
    rf"|(?P<word>{_WORD})"
)


def parse_line(text):
    """Return ``(numbers, labels)`` found in one serial data line.

    Numbers are returned as the matched strings; ``float()`` accepts all
    of them.
    """
    numbers = []
    labels = []
    for match in TOKEN_PATTERN.finditer(text):
        if match.lastgroup == "number":
            numbers.append(match.group("number"))
        else:
            labels.append(match.group(match.lastgroup))
    return numbers, labels


def parse_numbers(text):
    """Return numeric fields found in a serial data line."""
    return parse_line(text)[0]


def parse_labels(text):
    """Return labels found in a serial data line."""
    return parse_line(text)[1]
