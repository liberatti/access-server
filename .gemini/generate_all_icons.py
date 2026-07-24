from PIL import Image
import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
source_path = os.path.join(base_dir, "_docs/access-server-logo-monogram.png")
output_dir = os.path.join(base_dir, "web/assets")
os.makedirs(output_dir, exist_ok=True)

img = Image.open(source_path).convert("RGBA")

# Crop ONLY the 'A' monogram emblem (excluding text at bottom)
crop_box = (260, 260, 740, 640)
emblem = img.crop(crop_box)

# Make dark background transparent
datas = emblem.getdata()
new_data = []

for r, g, b, a in datas:
    # Check if color is part of dark background (deep navy / dark blue / near black)
    # Background color is roughly RGB(11, 19, 43) or lower luminance
    if r < 35 and g < 40 and b < 65:
        new_data.append((0, 0, 0, 0))  # Fully transparent
    elif r < 50 and g < 55 and b < 85:
        # Smooth transition for anti-aliasing edge pixels
        alpha = int(255 * ((r + g + b) / 190))
        new_data.append((r, g, b, min(255, max(0, alpha))))
    else:
        new_data.append((r, g, b, a))

emblem.putdata(new_data)

# Center onto a square transparent canvas 480x480
transparent_canvas = Image.new("RGBA", (480, 480), (0, 0, 0, 0))
offset_y = (480 - emblem.height) // 2
transparent_canvas.paste(emblem, (0, offset_y), emblem)

sizes = {
    "icon.png": (512, 512),
    "android-chrome-512x512.png": (512, 512),
    "android-chrome-192x192.png": (192, 192),
    "apple-touch-icon.png": (180, 180),
    "favicon-32x32.png": (32, 32),
    "favicon-16x16.png": (16, 16),
}

for name, size in sizes.items():
    resized = transparent_canvas.resize(size, Image.Resampling.LANCZOS)
    resized.save(os.path.join(output_dir, name))

# Save favicons
transparent_canvas.resize((48, 48), Image.Resampling.LANCZOS).save(os.path.join(output_dir, "favicon.ico"), format="ICO")
transparent_canvas.resize((48, 48), Image.Resampling.LANCZOS).save(os.path.join(base_dir, "web/favicon.ico"), format="ICO")

print("Successfully generated transparent background monogram logo icons!")
