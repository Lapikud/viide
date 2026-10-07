# original script

import qrcode

url = input("Enter the URL or text: ").strip()

file_path = input("Enter file path (qrcode.png): ").strip() or "qrcode.png"

img = qrcode.make(url)
img.save(file_path)

print(f"QR Code was generated and saved as {file_path}!")
