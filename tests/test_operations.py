import tempfile
import unittest
from pathlib import Path
from stageos.operations import create_document, save_document, import_file, trash_file, restore_file, safe_name

class OperationsTests(unittest.TestCase):
    def test_create_save_trash_restore(self):
        with tempfile.TemporaryDirectory() as td:
            base=Path(td); lib=base/'library'; trash=base/'trash'
            p=create_document(lib,'Låt');save_document(lib,p.name,'Vers 1\nRefräng')
            self.assertEqual(p.read_text(), 'Vers 1\nRefräng')
            deleted=trash_file(lib,trash,p.name)
            self.assertFalse(p.exists())
            self.assertEqual(restore_file(lib,deleted),p)
    def test_reject_escape(self):
        for name in ('../escape','/etc/passwd','a/b','..',''):
            with self.assertRaises(ValueError):safe_name(name)
    def test_import_collision_and_symlink(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);source=root/'song.mp3';source.write_bytes(b'fake')
            dest=import_file(root/'library',source)
            self.assertTrue(dest.exists())
            with self.assertRaises(FileExistsError):import_file(root/'library',source)
            link=root/'link.mp3';link.symlink_to(source)
            with self.assertRaises(ValueError):import_file(root/'library',link)
    def test_no_overwrite(self):
        with tempfile.TemporaryDirectory() as td:
            create_document(Path(td),'song')
            with self.assertRaises(FileExistsError):create_document(Path(td),'song')
if __name__=='__main__':unittest.main()
