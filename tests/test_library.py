import tempfile
import unittest
from pathlib import Path
from stageos.library import list_media, read_text

class LibraryTests(unittest.TestCase):
    def test_list_filters_and_sorts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for name in ('b.mp3','A.txt','ignore.exe'):(root/name).write_text('x')
            (root/'link.txt').symlink_to(root/'A.txt')
            self.assertEqual([p.name for p in list_media(root)],['A.txt','b.mp3'])
    def test_read_utf8(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'song.txt';p.write_text('Hej\nVärlden',encoding='utf-8')
            self.assertEqual(read_text(p),['Hej','Världen'])
    def test_reject_oversized_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'song.txt';p.write_bytes(b'x'*(2*1024*1024+1))
            with self.assertRaises(ValueError):read_text(p)

if __name__=='__main__':unittest.main()
