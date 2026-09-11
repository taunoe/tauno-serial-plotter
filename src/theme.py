"""Application theme, platform colors, and bundled icon paths."""

import logging
import os
import platform
import subprocess
from dataclasses import dataclass

from PyQt6 import QtCore, QtWidgets


PLOT_COLORS = [
    "#ba8310", "#00BCD4", "#3F51B5", "#E91E63", "#FF9800",
    "#9C27B0", "#4CAF50", "#FFC107", "#f44336", "#03A9F4",
    "#FFEB3B", "#CDDC39", "#2196F3", "#8BC34A", "#009688",
]


def _system_theme(app):
    """Return the platform color scheme, defaulting to light."""
    scheme = app.styleHints().colorScheme()
    if scheme == QtCore.Qt.ColorScheme.Dark:
        return "dark"
    return "light"


def _system_accent_color(dark):
    """Return the GNOME accent color, with a portable fallback."""
    accent_colors = {
        "blue": ("#62A0EA", "#3584E4"),
        "teal": ("#5BC8AF", "#2190A4"),
        "green": ("#57E389", "#33D17A"),
        "yellow": ("#F8E45C", "#F6D32D"),
        "orange": ("#FFBE6F", "#FF7800"),
        "red": ("#FF7B63", "#E01B24"),
        "pink": ("#DC8ADD", "#C061CB"),
        "purple": ("#C061CB", "#9141AC"),
        "slate": ("#949390", "#5E5C64"),
    }
    try:
        result = subprocess.run(
            ["gsettings", "get", "org.gnome.desktop.interface", "accent-color"],
            check=False,
            capture_output=True,
            text=True,
            timeout=1,
        )
        accent = result.stdout.strip().strip("'")
        if accent in accent_colors:
            return accent_colors[accent][0 if dark else 1]
    except (OSError, subprocess.SubprocessError):
        logging.debug("GNOME accent color is unavailable", exc_info=True)
    return "#9CCC65" if dark else "#62A0EA"


@dataclass(frozen=True)
class Theme:
    """Resolved colors and resource paths for one application session."""

    dark: bool
    colors: dict
    icons: dict
    plot_colors: list


def create_theme(app):
    """Resolve the theme after QApplication has loaded platform settings."""
    dark = _system_theme(app) == "dark"
    if dark:
        colors = {
            "oranz": "#FF6F00",
            "accent": _system_accent_color(True),
            "dark": "#1d1d20",
            "hall": "#B0BEC5",
            "black": "#212121",
            "foreground": "#B0BEC5",
        }
    else:
        colors = {
            "oranz": "#C64600",
            "accent": _system_accent_color(False),
            "dark": "#F6F5F4",
            "hall": "#FFFFFF",
            "black": "#2E3436",
            "foreground": "#2E3436",
        }

    if platform.system() == "Windows":
        icon_dir = os.path.join(".", "icons")
    else:
        icon_dir = os.path.join(os.path.dirname(__file__), "icons")
    icon_names = {
        "logo": "tauno-serial-plotter.svg",
        "minus": "minus.svg",
        "plus": "plus.svg",
        "arrow_down": "arrow_down.svg",
        "about": "help-about-symbolic.svg",
        "clean": "larger-brush-symbolic.svg",
        "size": "ruler-end-horizontal-left-symbolic.svg",
    }
    icons = {name: os.path.join(icon_dir, filename)
             for name, filename in icon_names.items()}
    return Theme(dark, colors, icons, PLOT_COLORS)
