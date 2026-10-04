"""Unit tests for theme resolution and generated widget styles."""

import unittest
from unittest.mock import patch

from PyQt6.QtWidgets import QApplication

from src.theme import _system_accent_color, create_theme
from src.widgets import create_styles


class ThemeAndStylesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.application = QApplication.instance() or QApplication([])

    def test_light_theme_uses_light_palette_and_accent(self):
        with patch("src.theme._system_theme", return_value="light"), \
                patch("src.theme._system_accent_color", return_value="#123456"):
            theme = create_theme(self.application)

        self.assertFalse(theme.dark)
        self.assertEqual(theme.colors["gray"], "#FFFFFF")
        self.assertEqual(theme.colors["orange"], "#C64600")
        self.assertEqual(theme.colors["accent"], "#123456")

    def test_dark_theme_uses_dark_palette_and_accent(self):
        with patch("src.theme._system_theme", return_value="dark"), \
                patch("src.theme._system_accent_color", return_value="#654321"):
            theme = create_theme(self.application)

        self.assertTrue(theme.dark)
        self.assertEqual(theme.colors["gray"], "#B0BEC5")
        self.assertEqual(theme.colors["orange"], "#FF6F00")
        self.assertEqual(theme.colors["accent"], "#654321")

    def test_accent_falls_back_when_gsettings_is_unavailable(self):
        with patch("src.theme.subprocess.run", side_effect=OSError):
            self.assertEqual(_system_accent_color(False), "#62A0EA")
            self.assertEqual(_system_accent_color(True), "#9CCC65")

    def test_generated_styles_use_resolved_theme_colors(self):
        with patch("src.theme._system_theme", return_value="light"), \
                patch("src.theme._system_accent_color", return_value="#123456"):
            theme = create_theme(self.application)

        styles = create_styles(theme)

        expected_style_names = {
            "btn_icon_style",
            "btn_icon_style_disabled",
            "btn_style",
            "btn_style_disabled",
            "label_style",
            "Qinfo_text_style",
            "dropdown_style",
            "dropdown_style_disabled",
            "QDoubleSpinBox_style",
        }
        self.assertEqual(set(styles), expected_style_names)
        self.assertIn(theme.colors["gray"], styles["btn_style"])
        self.assertIn(theme.colors["black"], styles["btn_style"])
        self.assertIn(theme.colors["gray"], styles["dropdown_style"])
        self.assertIn(theme.colors["black"], styles["dropdown_style"])
        self.assertIn(theme.colors["orange"], styles["btn_style"])
        self.assertNotIn("hall", "\n".join(styles.values()))
        self.assertNotIn("oranz", "\n".join(styles.values()))

    def test_theme_contains_paths_for_all_icons(self):
        theme = create_theme(self.application)

        self.assertEqual(
            set(theme.icons),
            {"logo", "minus", "plus", "arrow_down", "about", "clean", "size"},
        )
        for icon_path in theme.icons.values():
            self.assertTrue(icon_path.endswith(".svg"))


if __name__ == "__main__":
    unittest.main()
