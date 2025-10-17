#!/usr/bin/env bash
set -e

# Install prerequisites for adding repository
sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates curl gnupg

GPG_KEY_PATH="/usr/share/keyrings/doppler-archive-keyring.gpg"
GPG_KEY_URL="https://packages.doppler.com/public/cli/gpg.DE2A7741A397C129.key"
DOPPLER_PKG_REPO_URL="https://packages.doppler.com/public/cli/deb/debian"
DOPPLER_DEB_LINE="deb [signed-by=$GPG_KEY_PATH] $DOPPLER_PKG_REPO_URL any-version main"
SRC_DIR="/etc/apt/sources.list.d"
SRC_FILE="$SRC_DIR/doppler-cli.list"

# ensure sources directory exists
if [ ! -d "$SRC_DIR" ]; then
    sudo mkdir -p "$SRC_DIR"
fi

# add doppler gpg key only if it's not already present
if [ ! -f "$GPG_KEY_PATH" ]; then
    echo "Installing Doppler GPG key..."
    curl -sLf --retry 3 --tlsv1.2 --proto "=https" "$GPG_KEY_URL" | sudo gpg --dearmor -o "$GPG_KEY_PATH"
else
    echo "Doppler GPG key already present; skipping."
fi

# add doppler apt source only if it's not already present, and run update only when added
if [ -f "$SRC_FILE" ] && grep -Fxq "$DOPPLER_DEB_LINE" "$SRC_FILE"; then
    echo "Doppler APT source already present; skipping add/update."
else
    echo "Adding Doppler APT source..."
    echo "$DOPPLER_DEB_LINE" | sudo tee "$SRC_FILE" >/dev/null
    sudo apt-get update
fi

# If Doppler is already installed, skip everything
if command -v doppler >/dev/null 2>&1; then
    echo "Doppler already installed; skipping."
else
    sudo apt-get install -y doppler
    echo "Doppler installed successfully."
fi
