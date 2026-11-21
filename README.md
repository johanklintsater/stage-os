# STAGE OS 0.7 — Studio Desktop (experimental)

A lightweight desktop prototype for older 64-bit PCs, musicians, setlists, teleprompters, and text documents. **This is not yet a tested, installable operating-system release.** The underlying Linux distribution is Debian-based but users should eventually install STAGE OS from one USB image.

## Features in source
- Mouse/keyboard-driven Tkinter desktop with several independent lyric windows
- TXT/Markdown editing, setlists, auto-scroll and fullscreen
- MP3/WAV/FLAC/OGG playback through the external mpv player, separate from text windows
- Local file import, rename, trash and restore
- ZIP text backups with size, extension, traversal and overwrite checks
- NetworkManager Wi-Fi/Ethernet launcher; SFTP can be enabled with OpenSSH by an administrator (SSH is disabled by default in the candidate image)
- Experimental Debian 13 `live-build` recipe (not validated as an installable ISO)

## Local developer tests
On a Linux desktop with Python 3, Tkinter and mpv installed:

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q stageos
bash -n iso/build-iso.sh
python3 -m stageos.desktop
```

## ISO candidate — only in a disposable Debian 13 amd64 VM

```bash
sudo bash iso/build-iso.sh
```

The build script requires Debian 13 (trixie) and root privileges **inside an isolated build machine**. It does not format disks, but the Debian Installer included in the resulting live image can erase the selected disk. **Do not install it on a PC containing important data.** The image still needs boot tests for BIOS/UEFI, persistence, Wi-Fi, Ethernet, audio, login/session and installer behavior.

## GitHub Actions
- **Tests** runs Python unit tests and syntax checks on pushes and pull requests.
- **Candidate ISO build** is **manual only** (Actions → Candidate ISO build → Run workflow), and is unverified. An artifact is not proof of a safe installer.
- Do not publish an ISO as a stable release until VM and physical-hardware acceptance tests pass.

## Release checklist
1. Build candidate ISO successfully; test on BIOS and UEFI virtual machines.
2. Test installer using disposable virtual disks; review disk selection and data-loss warnings.
3. Verify startup to desktop, stable mouse/keyboard, data persistence, audio and text playback.
4. Test Ethernet, hardware-specific Wi-Fi firmware and SFTP with key-only authentication.
5. Add safe update/rollback process, accessibility and backup-recovery documentation.

Open-source under MIT License. Contributions welcome.