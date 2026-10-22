"""Regression checks for source preservation, reference figures and map selection.

Run: python -m unittest test_app.py
"""
import hashlib
import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest

from app import REFERENCE, load_tuition


class StoryTests(unittest.TestCase):
    def test_source_assets_unchanged(self):
        expected = {
            "Canadian_student.csv": "F0F7A21185E67EA510337A9FA3E0AE9DC356CC5BEC1270DEBFE8C5B9E62C462D",
            "International_student.csv": "ADE8D173AF39B797AEE6513EAA73BD5785C405D71FDDE84E8B397A98CE29E5A9",
            "graduate_tuition_region.csv": "06B89D149519FD0A19C0FD300EA74E8945AA9B5C8C426BB5B4EC500518B358FE",
            "undergrad_tuition_region.csv": "09D9E90721A9A7F9620E8B0458A54D06D39712F059A5A7908C3848DDCAC749A1",
            "tuition_trend.png": "58024AA695320300F9FBC449F6879C716F232D0B7DD6AA19EC7429E57AE2D83F",
            "domestic_tuition_map.png": "D8EF9FE5DCE7661D796AF9D8D1DC9096EA66F6B7406C242263CC1DF9125CE852",
            "international_tuition_map.png": "B68A2D64E9654442157DEEDDCE31630F8DC8408AD7231DBF12C0487577924738",
        }
        for filename, checksum in expected.items():
            self.assertEqual(hashlib.sha256(Path(filename).read_bytes()).hexdigest().upper(), checksum)

    def test_evidence_and_arithmetic(self):
        self.assertEqual(sum(REFERENCE.values()), 2121)
        self.assertEqual(sum(REFERENCE.values()) - 23448 / 12, 167)
        domestic, international, graduate = load_tuition()
        self.assertEqual(international.loc[2025].iloc[0] - domestic.loc[2025].iloc[0], 34012)
        self.assertEqual(graduate.drop(index="Canada")["International students"].idxmax(), "Ontario")

    def test_story_and_map_interactions(self):
        app = AppTest.from_file("app.py", default_timeout=30).run()
        self.assertFalse(app.exception)
        self.assertIn('Part III: Making Ends Meet', [heading.value for heading in app.header])
        self.assertEqual(len(app.number_input), 0)
        self.assertEqual(len(app.slider), 0)
        app.segmented_control(key="map_group").set_value("Domestic").run()
        self.assertEqual(app.segmented_control(key="map_group").value, "Domestic")
        self.assertFalse(app.exception)


if __name__ == "__main__":
    unittest.main()
