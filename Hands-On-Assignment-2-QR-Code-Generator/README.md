# Hands-On Assignment 2 — AI QR Code Generator

A command-line application that takes a URL address and writes it out as a QR
code image. A QR (quick-response) code, invented by Denso Wave in 1994, stores
data in a two-dimensional grid of modules together with Reed-Solomon
error-correction codewords, so a camera can recover the payload even when part
of the symbol is damaged or obscured.

The default URL is the assignment's target, <https://www.bioxsystems.com/>.

## Files

| File | Description |
|------|-------------|
| `qr_generator.py` | The application — URL normalization, validation, QR encoding and PNG output |
| `requirements.txt` | Manifest listing the `qrcode[pil]` dependency |
| `Hands-On Assignment 2 - AI QR Code Generator.docx` | Assignment report |
| `www_bioxsystems_com_qr.png` | Generated QR code for https://www.bioxsystems.com/ |
| `www_ucumberlands_edu_qr.png` | Generated QR code for https://www.ucumberlands.edu/ |
| `screenshot_setup.png` | Terminal — creating the environment and installing from the manifest |
| `screenshot_run_default.png` | Terminal — interactive run encoding the Biox Systems URL |
| `screenshot_run_argument.png` | Terminal — URL passed as an argument, and the validation error |
| `screenshot_help.png` | Terminal — the command-line help |

## Setup

Python 3.8 or newer is required. Create a virtual environment and install the
dependency from the manifest:

```bash
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
```

## Running

Prompt for the URL — pressing Enter accepts the Biox Systems default:

```bash
python3 qr_generator.py
```

Or pass the URL directly, optionally choosing the output file:

```bash
python3 qr_generator.py https://www.ucumberlands.edu/ -o campus_qr.png
```

A scheme is filled in when it is omitted, so `www.bioxsystems.com` is encoded
as `https://www.bioxsystems.com`. The program writes a PNG named after the host
unless `-o` says otherwise, and exits with status 1 on an unusable URL.

## How it works

`qrcode.QRCode` is created with `version=None` so the library picks the
smallest symbol version the data fits into, and with error correction level H,
the highest of the four levels, which reserves enough redundancy to restore
about 30% of the codewords. Each module is drawn 10 pixels wide and the symbol
is surrounded by the four-module quiet zone the QR specification requires, so
the Biox Systems URL comes out as a 410 × 410 pixel image.
