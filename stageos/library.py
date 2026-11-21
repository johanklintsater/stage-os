"""Library utilities. Only regular files within the library are indexed."""
from pathlib import Path
TEXT_EXT = {'.txt', '.md'}
AUDIO_EXT = {'.mp3', '.wav', '.flac', '.ogg', '.opus', '.m4a'}
MAX_TEXT_BYTES = 2 * 1024 * 1024

def list_media(root: Path):
    root = root.resolve()
    if not root.is_dir(): return []
    result = []
    for p in root.iterdir():
        if p.is_symlink() or not p.is_file(): continue
        if p.suffix.lower() not in TEXT_EXT | AUDIO_EXT: continue
        result.append(p)
    return sorted(result, key=lambda p: p.name.casefold())

def read_text(path: Path):
    if path.suffix.lower() not in TEXT_EXT: raise ValueError('Inte en textfil')
    if path.stat().st_size > MAX_TEXT_BYTES: raise ValueError('Textfilen är för stor')
    return path.read_text(encoding='utf-8-sig').splitlines()
