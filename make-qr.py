#!/usr/bin/env python3
"""
URL -> QR code PNG.

Usage:
  python3 make-qr.py <url> [out.png]
  python3 make-qr.py            # interactive: paste URL, get qr-<timestamp>.png
"""
import sys, time
import qrcode

def main():
    if len(sys.argv) > 1:
        url = sys.argv[1]
        out = sys.argv[2] if len(sys.argv) > 2 else "qr-%s.png" % time.strftime("%H%M%S")
    else:
        url = input("URL: ").strip()
        out = "qr-%s.png" % time.strftime("%H%M%S")
    if not url:
        sys.exit("no URL given")
    img = qrcode.make(url, error_correction=qrcode.constants.ERROR_CORRECT_L,
                      box_size=8, border=4)
    img.save(out)
    print("saved %s  (%d chars)" % (out, len(url)))

if __name__ == "__main__":
    main()
