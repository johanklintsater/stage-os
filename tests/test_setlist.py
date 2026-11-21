import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch
from stageos.desktop import Desktop

class SetlistTests(unittest.TestCase):
    def test_load_missing(self):
        with tempfile.TemporaryDirectory() as d:
            desk=Desktop.__new__(Desktop)
            desk.setlist_path=Path(d)/'setlist.json'
            self.assertEqual(desk.load_setlist(),[])
    def test_save_reload(self):
        with tempfile.TemporaryDirectory() as d:
            desk=Desktop.__new__(Desktop)
            desk.setlist_path=Path(d)/'setlist.json'
            desk.setlist=['Låt 1.txt','Låt 2.md']
            desk.save_setlist()
            self.assertEqual(desk.load_setlist(),desk.setlist)
    def test_reject_path_in_setlist(self):
        with tempfile.TemporaryDirectory() as d:
            desk=Desktop.__new__(Desktop)
            desk.setlist_path=Path(d)/'setlist.json'
            desk.setlist_path.write_text('["../secret.txt", "valid.txt"]')
            self.assertEqual(desk.load_setlist(),['valid.txt'])
