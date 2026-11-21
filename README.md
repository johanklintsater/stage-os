# STAGE OS 0.8 Beta — Studio Desktop (experimental)

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
- **STAGE OS 0.8 Beta ISO** runs on changes and can be triggered manually. Its Actions artifact is automatically ZIP-wrapped by GitHub. To publish a direct `.iso` as a prerelease, use **Run workflow** on the development branch with `publish_release=true` only after security review. The resulting file appears under GitHub **Releases**, not **Actions → Artifacts**. Neither a successful build nor a SHA-256 match proves the ISO is malware-free.
- Do not publish an ISO as a stable release until VM and physical-hardware acceptance tests pass.

## Release checklist
1. Build candidate ISO successfully; test on BIOS and UEFI virtual machines.
2. Test installer using disposable virtual disks; review disk selection and data-loss warnings.
3. Verify startup to desktop, stable mouse/keyboard, data persistence, audio and text playback.
4. Test Ethernet, hardware-specific Wi-Fi firmware and SFTP with key-only authentication.
5. Add safe update/rollback process, accessibility and backup-recovery documentation.

Open-source under MIT License. Contributions welcome.
## 0.8 Beta acceptance tests
- Boot ISO in a disposable VirtualBox VM; check login, startup screen, clock, all four tiles, and window management.
- Import and play two audio files: each must stop at end; next file must never auto-play.
- Check sound output, volume, wired network and Wi-Fi on supported hardware.
- Check file import, edit, save, trash, restore, and reboot persistence separately.
- Verify SHA256SUMS and inspect security scanner warnings before distribution. Do not bypass browser protections.
- 32-bit Legacy, MIDI foot control and remote tablet display remain future work.
