"""Versioned local backups with safe extraction, no shell commands."""
from pathlib import Path
from datetime import datetime, timezone
from zipfile import ZipFile, ZIP_DEFLATED
from .library import TEXT_EXT, MAX_TEXT_BYTES
from .operations import safe_name, validate_target

def backup_texts(library, destination):
    library, destination = Path(library).resolve(), Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    filename = 'stageos-texts-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '.zip'
    archive = destination / filename
    with ZipFile(archive, 'x', compression=ZIP_DEFLATED) as z:
        for p in sorted(library.iterdir()):
            if p.is_symlink() or not p.is_file() or p.suffix.lower() not in TEXT_EXT: continue
            if p.stat().st_size > MAX_TEXT_BYTES: continue
            z.write(p, arcname=p.name)
    return archive

def restore_texts(library, archive):
    library = Path(library).resolve()
    library.mkdir(parents=True, exist_ok=True)
    imported = []
    with ZipFile(archive) as z:
        entries = z.infolist()
        if len(entries) > 5000: raise ValueError('För många filer')
        names = set()
        for item in entries:
            name = safe_name(item.filename)
            if name in names or Path(name).suffix.lower() not in TEXT_EXT or item.is_dir() or item.file_size > MAX_TEXT_BYTES:
                raise ValueError('Ogiltigt arkivinnehåll')
            names.add(name)
            target = validate_target(library, name)
            if target.exists(): raise FileExistsError(target)
        for item in entries:
            target = validate_target(library, item.filename)
            with z.open(item) as source, target.open('xb') as out:
                remaining = MAX_TEXT_BYTES + 1
                while remaining:
                    block = source.read(min(65536, remaining))
                    if not block: break
                    out.write(block)
                    remaining -= len(block)
                if remaining == 0:
                    target.unlink(missing_ok=True)
                    raise ValueError('För stor fil')
            imported.append(target)
    return imported
