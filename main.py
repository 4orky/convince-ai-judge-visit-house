"""A one-picture invitation: carry entry.png into the output folder.
The picture itself is the whole entry, a letter asking the AI judge to
visit my house, drawn once and shipped beside this script. Nothing here
redraws it: the program reads the shipped bytes, walks every PNG chunk
to prove the file is intact, then writes those exact bytes out again,
so the delivered file matches the shipped one on every run. It uses
only the Python standard library, never touches the network, and takes
its only setting, the output folder, from its first argument or from
the MAKEFUN_OUTPUT_DIR environment variable, falling back to /output."""
from hashlib import sha256
from os import environ, makedirs, remove, replace
from os.path import abspath, dirname, join
from sys import argv, stderr
import zlib
ENTRY_NAME = "entry.png"
BYTE_CEILING = 1024 * 1024
EDGE_CEILING = 1024
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
KNOWN_DEPTHS = (1, 2, 4, 8, 16)
KNOWN_COLOURS = (0, 2, 3, 4, 6)
def fingerprint(payload):
    return sha256(payload).hexdigest()
def fail(message):
    stderr.write("cannot deliver entry: " + message + "\n")
    raise SystemExit(1)
def walk_chunks(payload):
    cursor = len(PNG_SIGNATURE)
    seen = []
    while cursor < len(payload):
        if cursor + 12 > len(payload):
            fail("chunk header at offset %d runs past the end of the file" % cursor)
        size = int.from_bytes(payload[cursor:cursor + 4], "big")
        kind = payload[cursor + 4:cursor + 8]
        end = cursor + 12 + size
        if end > len(payload):
            fail("chunk %s at offset %d claims %d bytes but the file ends first" % (kind.decode("latin-1"), cursor, size))
        stored = int.from_bytes(payload[end - 4:end], "big")
        actual = zlib.crc32(payload[cursor + 4:end - 4]) & 0xFFFFFFFF
        if stored != actual:
            fail("chunk %s at offset %d fails its CRC check" % (kind.decode("latin-1"), cursor))
        seen.append((kind.decode("latin-1"), size, payload[cursor + 8:end - 4]))
        cursor = end
        if kind == b"IEND":
            break
    return seen, payload[cursor:]
def inspect_picture(payload):
    if len(payload) > BYTE_CEILING:
        fail("entry.png is %d bytes, above the %d byte limit" % (len(payload), BYTE_CEILING))
    if payload[:len(PNG_SIGNATURE)] != PNG_SIGNATURE:
        fail("entry.png does not start with the PNG signature")
    chunks, tail = walk_chunks(payload)
    kinds = [kind for kind, _size, _body in chunks]
    if not kinds or kinds[0] != "IHDR":
        fail("the first chunk is not IHDR, so this is not a usable PNG")
    if kinds[-1] != "IEND":
        fail("the last chunk is not IEND, so the picture is cut short")
    if tail.strip(b"\x00"):
        fail("unexpected bytes follow the IEND chunk")
    header = chunks[0][2]
    if len(header) != 13:
        fail("the IHDR chunk is %d bytes instead of 13" % len(header))
    width = int.from_bytes(header[0:4], "big")
    height = int.from_bytes(header[4:8], "big")
    depth = header[8]
    colour = header[9]
    method = header[10]
    filtering = header[11]
    interlace = header[12]
    if width == 0 or height == 0:
        fail("the picture reports a zero width or height")
    if width > EDGE_CEILING or height > EDGE_CEILING:
        fail("the picture is %d by %d, above the %d pixel edge limit" % (width, height, EDGE_CEILING))
    if depth not in KNOWN_DEPTHS:
        fail("bit depth %d is not a PNG bit depth" % depth)
    if colour not in KNOWN_COLOURS:
        fail("colour type %d is not a PNG colour type" % colour)
    if method != 0 or filtering != 0:
        fail("compression method %d and filter method %d are not the PNG defaults" % (method, filtering))
    if interlace not in (0, 1):
        fail("interlace method %d is not a PNG interlace method" % interlace)
    if "IDAT" not in kinds:
        fail("the picture carries no IDAT chunk, so it holds no pixels")
    if colour == 3 and "PLTE" not in kinds:
        fail("colour type 3 needs a PLTE chunk, but none is present")
    if colour in (0, 4) and "PLTE" in kinds:
        fail("colour type %d must not carry a PLTE chunk" % colour)
    idat_bytes = sum(size for kind, size, _body in chunks if kind == "IDAT")
    return width, height, chunks, idat_bytes, len(tail)
def deliver_entry():
    script_folder = dirname(abspath(__file__))
    shipped = join(script_folder, ENTRY_NAME)
    try:
        payload = open(shipped, "rb").read()
    except OSError as problem:
        fail("cannot read %s: %s" % (shipped, problem))
    width, height, chunks, idat_bytes, padding = inspect_picture(payload)
    if len(argv) > 1:
        output_folder = argv[1]
    elif environ.get("MAKEFUN_OUTPUT_DIR"):
        output_folder = environ["MAKEFUN_OUTPUT_DIR"]
    else:
        output_folder = "/output"
    try:
        makedirs(output_folder, exist_ok=True)
    except OSError as problem:
        fail("cannot create %s: %s" % (output_folder, problem))
    destination = join(output_folder, ENTRY_NAME)
    staging = destination + ".staging"
    try:
        with open(staging, "wb") as handle:
            handle.write(payload)
        replace(staging, destination)
    except OSError as problem:
        try:
            remove(staging)
        except OSError:
            pass
        fail("cannot write %s: %s" % (destination, problem))
    try:
        delivered = open(destination, "rb").read()
    except OSError as problem:
        fail("cannot read back %s: %s" % (destination, problem))
    if delivered != payload:
        fail("the delivered bytes differ from the shipped picture")
    for position, (kind, size, _body) in enumerate(chunks):
        print("chunk %d: %s, %d bytes" % (position, kind, size))
    print("delivered %s: %d bytes, %d by %d pixels, %d chunks, %d IDAT bytes, %d padding bytes, sha256 %s" % (destination, len(payload), width, height, len(chunks), idat_bytes, padding, fingerprint(payload)))
if __name__ in ("__main__",):
    deliver_entry()
