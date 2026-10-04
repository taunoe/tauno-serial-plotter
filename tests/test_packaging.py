"""Tests for package metadata and release-version consistency."""

import ast
import re
import unittest
import xml.etree.ElementTree as ElementTree
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - supported by newer test runtimes
    tomllib = None


ROOT = Path(__file__).parents[1]


class PackagingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if tomllib is None:
            raise unittest.SkipTest("Python tomllib is required for packaging tests")
        with (ROOT / "pyproject.toml").open("rb") as file:
            cls.project = tomllib.load(file)["project"]
        cls.version = cls.project["version"]

    def test_project_declares_runtime_dependencies(self):
        self.assertEqual(self.project["requires-python"], ">=3.7")
        self.assertEqual(
            set(self.project["dependencies"]),
            {"PyQt6", "pyqtgraph", "pyserial"},
        )

    def test_console_script_points_to_importable_main(self):
        self.assertEqual(
            self.project["scripts"]["tauno-serial-plotter"],
            "src.tauno_serial_plotter:main",
        )
        self.assertTrue((ROOT / "src" / "tauno_serial_plotter.py").is_file())
        self.assertTrue((ROOT / "src" / "tauno-serial-plotter.py").is_file())

    def test_package_data_includes_icons(self):
        package_data = tomllib.loads(
            (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        )["tool"]["setuptools"]["package-data"]
        self.assertEqual(package_data["src"], ["icons/*"])

    def test_runtime_version_matches_project_metadata(self):
        tree = ast.parse(
            (ROOT / "src" / "tauno_serial_plotter.py").read_text(encoding="utf-8")
        )
        versions = [
            node.value.value
            for node in ast.walk(tree)
            if isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name) and target.id == "VERSION"
                for target in node.targets
            )
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        ]
        self.assertEqual(versions, [self.version])

    def test_snap_version_matches_project_metadata(self):
        snapcraft = (ROOT / "snap" / "snapcraft.yaml").read_text(encoding="utf-8")
        self.assertRegex(snapcraft, rf"(?m)^version:\s*['\"]{re.escape(self.version)}['\"]$")

    def test_appstream_release_matches_project_metadata(self):
        appdata = ElementTree.parse(
            ROOT / "art.taunoerik.tauno-serial-plotter.appdata.xml"
        )
        release = appdata.getroot().find("./releases/release")
        self.assertIsNotNone(release)
        self.assertEqual(release.get("version"), self.version)


if __name__ == "__main__":
    unittest.main()
