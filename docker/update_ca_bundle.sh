#!/bin/sh
# The last certifi release that supports Python 2 ships a 2021 CA bundle. Replace it
# with the bundle from a current certifi release, which removes emSign ECC Root CA - G3
# and AAA Certificate Services (eMudhra intermediate key compromise, October 2026).
# requests, botocore and sentry-sdk all read certifi.where().
set -eu

VERSION=2026.10.19
URL=https://files.pythonhosted.org/packages/c4/51/29046e48f693c54e5b7412216d447a1d8362c9653148d98c02cdf65fa733/certifi-${VERSION}-py3-none-any.whl
SHA256=42d35340cc5b9ba78e818ddbff0c5b1c2b779de448a340fd1b989f5fa8670e1b
WHEEL=/tmp/certifi-${VERSION}-py3-none-any.whl

curl -sSfL --proto '=https' --proto-redir '=https' -o "$WHEEL" "$URL"
echo "$SHA256  $WHEEL" | sha256sum -c -

BUNDLE=$(python -c "import certifi; print(certifi.where())")
python -c "import sys, zipfile; open(sys.argv[2], 'wb').write(zipfile.ZipFile(sys.argv[1]).read('certifi/cacert.pem'))" "$WHEEL" "$BUNDLE"
rm "$WHEEL"

if grep -qE "emSign ECC Root CA - G3|CN=AAA Certificate Services" "$BUNDLE"; then
    echo "Compromised eMudhra trust anchors still present in $BUNDLE" >&2
    exit 1
fi
echo "Replaced $BUNDLE with the certifi $VERSION CA bundle"
