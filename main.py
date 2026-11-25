#!/usr/bin/env python3
"""convince-ai-judge-visit-house: write the invitation image to /output.

The entry is a single picture of a letter inviting the AI judge to visit
my house (entry.png, shipped in this repository). This program only copies
those exact bytes into the output directory, so every run produces the
identical file. It uses only the Python standard library and never touches
the network.
"""

import hashlib
import os
import struct
import sys
from pathlib import Path

SOURCE = Path(__file__).resolve().parent / "entry.png"
TARGET = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")) / "entry.png"
MAX_BYTES = 1024 * 1024
MAX_SIDE = 1024


def sha256_hex(data):
    digest = hashlib.sha256()
    digest.update(data)
    return digest.hexdigest()


def check_image(data):
    """Refuse anything that is not a whole PNG inside the bounty's caps."""
    if len(data) > MAX_BYTES:
        print("error: entry.png is %d bytes, over the 1 MiB cap"
              % len(data), file=sys.stderr)
        sys.exit(1)
    if data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        print("error: entry.png is not a PNG file", file=sys.stderr)
        sys.exit(1)
    # A truncated file still carries a valid header, so require the IEND
    # trailer too: without it the gate scorer would reject the image.
    if not data.rstrip(b"\x00").endswith(b"IEND\xaeB`\x82"):
        print("error: entry.png has no IEND trailer (truncated file)",
              file=sys.stderr)
        sys.exit(1)
    width, height = struct.unpack(">II", data[16:24])
    if width > MAX_SIDE or height > MAX_SIDE:
        print("error: entry.png is %dx%d, over the 1024x1024 cap"
              % (width, height), file=sys.stderr)
        sys.exit(1)
    return width, height


def main():
    if not SOURCE.exists():
        print("error: %s is missing from the repository" % SOURCE,
              file=sys.stderr)
        sys.exit(1)
    data = SOURCE.read_bytes()
    width, height = check_image(data)
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_bytes(data)
    if TARGET.read_bytes() != data:
        print("error: written bytes differ from entry.png", file=sys.stderr)
        sys.exit(1)
    print("wrote %s (%d bytes, %dx%d, sha256 %s)"
          % (TARGET, len(data), width, height, sha256_hex(data)))


if __name__ == "__main__":
    main()
