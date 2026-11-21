"""Safe local document operations; never follow symlinks."""
import os
import re
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from .library import TEXT_EXT, AUDIO_EXT, MAX_TEXT_BYTES

MAX_AUDIO_BYTES = 1024 * 1024 * 1024

def safe_name(name):
    if not isinstance(name, str) or not name or name in ('.', '..') or name != Path(name).name or '/' in name or "\\" in name or any(ord(c)<32 for c in name):
        raise ValueError('Ogiltigt filnamn')
    if len(name.encode('utf-8')) > 220: raise ValueError('För långt filnamn')
    return name

def validate_target(root, name):
    root=Path(root).resolve()
    safe_name(name)
    target=root/name
    if target.is_symlink():raise ValueError('Symboliska länkar är inte tillåtna')
    return target

def create_document(root, name):
    name=safe_name(name)
    if not Path(name).suffix: name += '.txt'
    if Path(name).suffix.lower() not in TEXT_EXT:raise ValueError('Endast TXT och MD')
    target=validate_target(root,name)
    target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('x',encoding='utf-8'):pass
    return target

def save_document(root, name, text):
    target=validate_target(root,name)
    if target.suffix.lower() not in TEXT_EXT:raise ValueError('Inte textfil')
    if not target.is_file():raise ValueError('Filen saknas')
    data=text.encode('utf-8')
    if len(data)>MAX_TEXT_BYTES:raise ValueError('För stor textfil')
    fd,tmp=tempfile.mkstemp(prefix='.stage-',dir=str(target.parent))
    try:
        with os.fdopen(fd,'wb') as out:
            out.write(data);out.flush();os.fsync(out.fileno())
        os.replace(tmp,target)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)
    return target

def import_file(root, source):
    source=Path(source)
    if source.is_symlink() or not source.is_file():raise ValueError('Inte en vanlig fil')
    target=validate_target(root,source.name)
    ext=source.suffix.lower()
    if ext not in TEXT_EXT|AUDIO_EXT:raise ValueError('Filtypen stöds inte')
    if source.stat().st_size > (MAX_TEXT_BYTES if ext in TEXT_EXT else MAX_AUDIO_BYTES):raise ValueError('För stor fil')
    if target.exists():raise FileExistsError(target)
    target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('xb') as out,source.open('rb') as inp:shutil.copyfileobj(inp,out,1024*1024)
    return target

def trash_file(root, trash, name):
    target=validate_target(root,name)
    if not target.is_file() or target.is_symlink():raise ValueError('Filen saknas')
    trash=Path(trash);trash.mkdir(parents=True,exist_ok=True)
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    dest=trash/(stamp+'_'+name)
    target.replace(dest)
    return dest

def restore_file(root, trash_path):
    trash_path=Path(trash_path)
    if not trash_path.is_file() or trash_path.is_symlink():raise ValueError('Ogiltig papperskorgsfil')
    match=re.match(r'^\d{8}T\d{12}Z_(.+)$',trash_path.name)
    if not match:raise ValueError('Ogiltigt papperskorgsnamn')
    target=validate_target(root,match.group(1))
    if target.exists():raise FileExistsError(target)
    trash_path.replace(target)
    return target
