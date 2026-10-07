"""Interactive QR code generator.

This standalone script prompts for text and an output path, then saves an image. It does
not use the Flask application.
"""

# original script

import qrcode

url = input("Enter the URL or text: ").strip()

file_path = input("Enter file path (qrcode.png): ").strip() or "qrcode.png"

img = qrcode.make(url)
img.save(file_path)

print(f"QR Code was generated and saved as {file_path}!")
