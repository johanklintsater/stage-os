#!/usr/bin/env bash
set -Eeuo pipefail
# Only build in a disposable Debian 13 amd64 VM/container.
[[ $EUID == 0 ]] || { echo 'Root required' >&2; exit 1; }
[[ $(uname -m) == x86_64 ]] || { echo 'amd64 required' >&2; exit 1; }
. /etc/os-release
[[ ${VERSION_CODENAME:-} == trixie ]] || { echo 'Debian 13 trixie required' >&2; exit 1; }
HERE=$(cd "$(dirname "$0")" && pwd)
PROJECT=$(cd "$HERE/.." && pwd)
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y live-build
mkdir -p "$PROJECT/build-work"
cd "$PROJECT/build-work"
lb config --distribution trixie --architectures amd64 --binary-images iso-hybrid --debian-installer live --debian-installer-gui false --archive-areas 'main non-free-firmware' --bootappend-live 'boot=live components quiet'
mkdir -p config/package-lists config/includes.chroot/opt/stageos config/includes.chroot/usr/share/xsessions config/includes.chroot/etc/lightdm/lightdm.conf.d config/includes.chroot/usr/local/bin config/includes.chroot/etc/skel/StageOS/library config/hooks/live
cat > config/package-lists/stageos.list.chroot <<'PACKAGES'
xorg xserver-xorg-video-all lightdm openbox python3 python3-tk fonts-dejavu-core network-manager network-manager-gnome openssh-server mpv alsa-utils pipewire pipewire-pulse wireplumber pavucontrol xterm dbus-x11 xdg-utils thunar firmware-iwlwifi firmware-realtek firmware-atheros
PACKAGES
cp "$PROJECT/stageos/"*.py config/includes.chroot/opt/stageos/
touch config/includes.chroot/opt/stageos/__init__.py
cat > config/includes.chroot/usr/local/bin/stageos-session <<'SESSION'
#!/bin/sh
openbox &
cd /opt
exec /usr/bin/python3 -m stageos.desktop
SESSION
chmod 755 config/includes.chroot/usr/local/bin/stageos-session
cat > config/includes.chroot/usr/share/xsessions/stageos.desktop <<'SESSION'
[Desktop Entry]
Name=STAGE OS
Comment=Stage OS lightweight desktop
Exec=/usr/local/bin/stageos-session
Type=Application
DesktopNames=STAGEOS
SESSION
cat > config/includes.chroot/etc/lightdm/lightdm.conf.d/50-stageos.conf <<'LIGHTDM'
[Seat:*]
user-session=stageos
LIGHTDM
cat > config/hooks/live/090-stageos-security.hook.chroot <<'SECURITY'
#!/bin/sh
set -eu
systemctl disable ssh.service 2>/dev/null || true
SECURITY
chmod +x config/hooks/live/090-stageos-security.hook.chroot
lb build
find . -maxdepth 1 -name '*.iso' -print
