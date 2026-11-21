import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile
from stageos.backup import backup_texts, restore_texts

class BackupTests(unittest.TestCase):
    def test_roundtrip(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t); lib = root/'lib'; lib.mkdir()
            (lib/'song.txt').write_text('Hello 🎸', encoding='utf-8')
            (lib/'ignore.exe').write_bytes(b'x')
            archive = backup_texts(lib, root/'backups')
            restored = root/'restore'
            self.assertEqual([p.name for p in restore_texts(restored, archive)], ['song.txt'])
            self.assertEqual((restored/'song.txt').read_text(), 'Hello 🎸')
    def test_traversal_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t); archive=root/'evil.zip'
            with ZipFile(archive,'w') as z: z.writestr('../evil.txt','bad')
            with self.assertRaises(ValueError): restore_texts(root/'lib', archive)
            self.assertFalse((root/'evil.txt').exists())
    def test_no_overwrite(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t); lib=root/'lib';lib.mkdir();(lib/'song.txt').write_text('original')
            archive=root/'backup.zip'
            with ZipFile(archive,'w') as z:z.writestr('song.txt','overwrite')
            with self.assertRaises(FileExistsError): restore_texts(lib,archive)
            self.assertEqual((lib/'song.txt').read_text(),'original')
