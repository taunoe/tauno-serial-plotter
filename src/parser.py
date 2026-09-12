"""Parsing helpers for serial plotter input."""

import re


NUMBER_PATTERN = re.compile(r"[-+]?[0-9]*\.?[0-9]+")
LABEL_PATTERN = re.compile(r"[-+]?[a-zA-Z]*\.?[a-zA-Z]+")


def parse_numbers(text):
    """Return numeric fields found in a serial data line."""
    return NUMBER_PATTERN.findall(text)


def parse_labels(text):
    """Return alphabetic labels found in a serial data line."""
    return LABEL_PATTERN.findall(text)
