#!/bin/bash
# build.sh — ai-coder-kimi Release-Build
# Erzeugt: dist/aicoder-kimi (binary), packaging/aicoder-kimi_*.deb
set -euo pipefail

VERSION=$(python3 -c "import tomllib; d=tomllib.load(open('pyproject.toml','rb')); print(d['project']['version'])")
ARCH=$(uname -m)
echo "Building aicoder-kimi v${VERSION} (${ARCH})..."

# venv falls nicht vorhanden
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    .venv/bin/pip install -e . -q
fi

# PyInstaller
.venv/bin/pip install pyinstaller -q
.venv/bin/pyinstaller aicoder.spec --distpath dist/ --workpath build/ --noconfirm -y 2>/dev/null

echo "Binary: $(ls -lh dist/aicoder-kimi | awk '{print $5, $9}')"

# Smoke-test
./dist/aicoder-kimi --help > /dev/null && echo "Binary: OK"

# Debian package (nur auf Debian/Ubuntu)
if command -v dpkg-deb &>/dev/null; then
    mkdir -p packaging/debian/aicoder-kimi/usr/bin
    cp dist/aicoder-kimi packaging/debian/aicoder-kimi/usr/bin/aicoder-kimi
    chmod 755 packaging/debian/aicoder-kimi/usr/bin/aicoder-kimi

    DEBFILE="packaging/aicoder-kimi_${VERSION}_$(dpkg --print-architecture).deb"
    dpkg-deb --build --root-owner-group packaging/debian/aicoder-kimi "$DEBFILE"

    SHA=$(sha256sum "$DEBFILE" | cut -d' ' -f1)
    echo "Debian: $DEBFILE (sha256=$SHA)"
fi

# Binary SHA für Release-Notes
BINSHA=$(sha256sum dist/aicoder-kimi | cut -d' ' -f1)
echo "Binary SHA256: $BINSHA"
echo ""
echo "Done. Install:"
echo "  sudo cp dist/aicoder-kimi /usr/bin/aicoder-kimi"
echo "  sudo dpkg -i $DEBFILE"
