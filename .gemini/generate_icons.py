from PIL import Image
import os

source_path = "_docs/access-server-logo-monogram.png"
output_dir = "web/assets"
os.makedirs(output_dir, exist_ok=True)

img = Image.open(source_path)

# Crop only the 'A' monogram emblem (excluding 'ACCESS SERVER' text)
crop_box = (250, 220, 750, 720)
logo_only = img.crop(crop_box)

sizes = {
    "icon.png": (512, 512),
    "android-chrome-512x512.png": (512, 512),
    "android-chrome-192x192.png": (192, 192),
    "apple-touch-icon.png": (180, 180),
    "favicon-32x32.png": (32, 32),
    "favicon-16x16.png": (16, 16),
}

for name, size in sizes.items():
    resized = logo_only.resize(size, Image.Resampling.LANCZOS)
    out_file = os.path.join(output_dir, name)
    resized.save(out_file)

ico_file = os.path.join(output_dir, "favicon.ico")
logo_only.resize((48, 48), Image.Resampling.LANCZOS).save(ico_file, format="ICO")
print("Icons successfully created in web/assets!")
