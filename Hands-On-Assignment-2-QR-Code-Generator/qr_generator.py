"""AI QR Code Generator.

Reads a URL address from the user and writes it out as a QR code image.

A QR (quick-response) code, invented by Denso Wave in 1994, is a
two-dimensional barcode: the payload is written into a grid of black and
white modules together with Reed-Solomon error-correction codewords, so a
camera can recover the text even when part of the symbol is damaged or
obscured.

The program can be used two ways:

    python3 qr_generator.py                       # prompt for the URL
    python3 qr_generator.py https://example.com   # take the URL as an argument

MSCS-633-M20 Advance Artificial Intelligence — Hands-On Assignment 2
Xhon Pelushi, University of the Cumberlands
"""

import argparse
import re
import sys
from urllib.parse import urlparse

import qrcode
from qrcode.constants import ERROR_CORRECT_H

# Appearance of the generated symbol. BOX_SIZE is the pixel size of a single
# module; BORDER is the width of the mandatory quiet zone, which the QR
# specification requires to be at least four modules wide so that scanners can
# find the edges of the symbol.
BOX_SIZE = 10
BORDER = 4
FILL_COLOR = "black"
BACK_COLOR = "white"

# The URL encoded when the user does not supply one of their own.
DEFAULT_URL = "https://www.bioxsystems.com/"

# Schemes a QR scanner will open as a web address.
ALLOWED_SCHEMES = ("http", "https")


def normalize_url(raw_url):
    """Return a cleaned-up URL, adding a scheme when the user omitted one.

    People habitually type "www.bioxsystems.com" rather than the full
    "https://www.bioxsystems.com/". A QR code holding the short form is still
    a valid QR code, but many scanners treat it as plain text instead of a
    link, so the scheme is filled in here.
    """
    url = raw_url.strip()
    if not url:
        raise ValueError("No URL was entered.")

    # A scheme is present only if the string starts with "something://".
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", url):
        url = "https://" + url

    return url


def validate_url(url):
    """Raise ValueError unless the URL is a usable http(s) web address."""
    parts = urlparse(url)

    if parts.scheme not in ALLOWED_SCHEMES:
        raise ValueError(
            f"Unsupported scheme '{parts.scheme}'. "
            f"Use one of: {', '.join(ALLOWED_SCHEMES)}."
        )

    # netloc is the host (and optional port). Without it there is nothing for
    # a scanner to open, e.g. "https:///path".
    if not parts.netloc:
        raise ValueError("The URL is missing a host name.")

    # A bare host with no dot ("https://localhost") is legal but is almost
    # always a typo in an assignment context, so it is rejected explicitly.
    if "." not in parts.netloc.split(":")[0]:
        raise ValueError(f"'{parts.netloc}' does not look like a host name.")

    return url


def make_qr_image(url):
    """Encode *url* and return the QR code as a PIL image.

    ``version=None`` lets the library pick the smallest symbol version (that
    is, the smallest grid) the data fits into. Error correction is set to the
    highest level, H, which reserves enough redundancy to restore about 30% of
    the codewords — useful for a code that will be printed, screenshotted or
    scanned at an angle.
    """
    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_H,
        box_size=BOX_SIZE,
        border=BORDER,
    )
    qr.add_data(url)

    # fit=True runs the version selection described above.
    qr.make(fit=True)

    return qr.make_image(fill_color=FILL_COLOR, back_color=BACK_COLOR)


def default_filename(url):
    """Derive a safe PNG file name from the host part of *url*.

    "https://www.bioxsystems.com/" becomes "www_bioxsystems_com_qr.png".
    """
    host = urlparse(url).netloc.split(":")[0]
    slug = re.sub(r"[^A-Za-z0-9]+", "_", host).strip("_").lower()
    return f"{slug or 'qrcode'}_qr.png"


def parse_arguments(argv):
    """Parse the command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate a QR code image from a URL address."
    )
    parser.add_argument(
        "url",
        nargs="?",
        help="URL to encode. If omitted, the program prompts for one.",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Name of the PNG file to write (default: derived from the URL).",
    )
    return parser.parse_args(argv)


def main(argv=None):
    """Run the generator. Returns a process exit status."""
    args = parse_arguments(argv if argv is not None else sys.argv[1:])

    print("AI QR Code Generator")
    print("-" * 44)

    # Take the URL from the command line when given, otherwise ask for it.
    # Pressing Enter at the prompt accepts the default URL.
    if args.url is not None:
        raw_url = args.url
    else:
        raw_url = input(f"Enter a URL [{DEFAULT_URL}]: ") or DEFAULT_URL

    try:
        url = validate_url(normalize_url(raw_url))
    except ValueError as error:
        # A bad URL is a user mistake, not a crash: report it plainly and
        # exit with a non-zero status so a script can detect the failure.
        print(f"Error: {error}", file=sys.stderr)
        return 1

    image = make_qr_image(url)
    output_path = args.output or default_filename(url)

    try:
        image.save(output_path)
    except OSError as error:
        print(f"Error: could not write '{output_path}': {error}", file=sys.stderr)
        return 1

    print(f"Encoded : {url}")
    print(f"Size    : {image.size[0]} x {image.size[1]} pixels")
    print(f"Saved   : {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
