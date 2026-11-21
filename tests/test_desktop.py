import unittest
from unittest.mock import patch, MagicMock
from stageos.desktop import Audio

class AudioTests(unittest.TestCase):
    @patch('stageos.desktop.subprocess.Popen')
    @patch('stageos.desktop.shutil.which',return_value='/usr/bin/mpv')
    def test_audio_uses_no_shell(self,_which,popen):
        proc=MagicMock();proc.poll.return_value=0;popen.return_value=proc
        audio=Audio();audio.play('/tmp/music.mp3')
        args,kwargs=popen.call_args
        self.assertEqual(args[0][-2:],['--','/tmp/music.mp3'])
        self.assertNotIn('shell',kwargs)
    @patch('stageos.desktop.shutil.which',return_value=None)
    def test_missing_mpv(self,_which):
        with self.assertRaises(RuntimeError):Audio().play('/tmp/music.mp3')

if __name__=='__main__':unittest.main()
