#!/usr/bin/env python3
import io
import os
import sys


DENSITY_FOREGROUND_SIZES = {
    "mipmap-mdpi": 108,
    "mipmap-hdpi": 162,
    "mipmap-xhdpi": 216,
    "mipmap-xxhdpi": 324,
    "mipmap-xxxhdpi": 432,
}

DENSITY_LAUNCHER_SIZES = {
    "mipmap-mdpi": 48,
    "mipmap-hdpi": 72,
    "mipmap-xhdpi": 96,
    "mipmap-xxhdpi": 144,
    "mipmap-xxxhdpi": 192,
}

BG_RGB = (13, 2, 20)  # #0d0214 Deep Violet Obsidian


def load_clean_logo(Image):
    with open("logo.png", "rb") as f:
        data = f.read()
    try:
        img = Image.open(io.BytesIO(data))
        img.load()
        return img.convert("RGBA")
    except Exception:
        # Repair extra 333-byte header chunk present in repository logo.png
        repaired = data[:33] + data[366:]
        img = Image.open(io.BytesIO(repaired))
        img.load()
        return img.convert("RGBA")


def build_foreground(img, size, Image):
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    safe_box = max(1, int(round(size * 0.68)))
    scale = min(safe_box / img.width, safe_box / img.height)
    new_w = max(1, int(round(img.width * scale)))
    new_h = max(1, int(round(img.height * scale)))
    resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    pos_x = (size - new_w) // 2
    pos_y = (size - new_h) // 2
    canvas.paste(resized, (pos_x, pos_y), resized)
    return canvas


def build_launcher_icon(img, size, is_round, Image, ImageDraw):
    bg = Image.new("RGBA", (size, size), (*BG_RGB, 255))
    fg_box = max(1, int(round(size * 0.76)))
    scale = min(fg_box / img.width, fg_box / img.height)
    new_w = max(1, int(round(img.width * scale)))
    new_h = max(1, int(round(img.height * scale)))
    resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    pos_x = (size - new_w) // 2
    pos_y = (size - new_h) // 2
    bg.paste(resized, (pos_x, pos_y), resized)

    if is_round:
        mask = Image.new("L", (size, size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size - 1, size - 1), fill=255)
        out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        out.paste(bg, (0, 0), mask)
        return out
    return bg


def resolve_density_size(folder_name, mapping, default_size):
    for key, val in mapping.items():
        if folder_name == key or folder_name.startswith(key + "-"):
            return val
    return default_size


def main():
    if not os.path.exists("logo.png"):
        print("logo.png not found, skipping icon generation")
        return

    try:
        from PIL import Image, ImageDraw
    except ImportError:
        print("PIL not found, installing pillow...")
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "--break-system-packages", "pillow"], check=True)
        from PIL import Image, ImageDraw

    logo_rgba = load_clean_logo(Image)
    res_dir = "./TMessagesProj/src/main/res"
    if not os.path.exists(res_dir):
        print(f"Res directory {res_dir} not found")
        return

    fg_count = 0
    launcher_count = 0
    for root, _, files in os.walk(res_dir):
        folder_name = os.path.basename(root)
        for file in files:
            full_path = os.path.join(root, file)
            if file.startswith("icon_foreground") and (file.endswith(".png") or file.endswith(".webp")):
                size = resolve_density_size(folder_name, DENSITY_FOREGROUND_SIZES, 432)
                fg_img = build_foreground(logo_rgba, size, Image)
                if file.endswith(".webp"):
                    fg_img.save(full_path, "WEBP", quality=95, method=6)
                else:
                    fg_img.save(full_path, "PNG", optimize=True)
                fg_count += 1
            elif file.startswith("ic_launcher") and (file.endswith(".png") or file.endswith(".webp")):
                size = resolve_density_size(folder_name, DENSITY_LAUNCHER_SIZES, 192)
                is_round = "round" in file
                icon_img = build_launcher_icon(logo_rgba, size, is_round, Image, ImageDraw)
                if file.endswith(".webp"):
                    icon_img.save(full_path, "WEBP", quality=95, method=6)
                else:
                    icon_img.save(full_path, "PNG", optimize=True)
                launcher_count += 1

    # Write Dark Purple background XML (#0d0214)
    bg_xml = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<shape xmlns:android="http://schemas.android.com/apk/res/android">\n'
        '    <solid android:color="#0d0214" />\n'
        '</shape>\n'
    )
    for bg_file in ["icon_background.xml", "icon_background_sa.xml"]:
        p = os.path.join(res_dir, "drawable", bg_file)
        if os.path.exists(os.path.dirname(p)):
            with open(p, "w", encoding="utf-8") as f:
                f.write(bg_xml)

    # Write clean adaptive icon XML (without monochrome paper plane)
    adaptive_xml = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">\n'
        '    <background android:drawable="@drawable/icon_background" />\n'
        '    <foreground android:drawable="@mipmap/icon_foreground" />\n'
        '</adaptive-icon>\n'
    )
    for icon_file in ["ic_launcher.xml", "ic_launcher_round.xml"]:
        p = os.path.join(res_dir, "mipmap-anydpi-v26", icon_file)
        if os.path.exists(os.path.dirname(p)):
            with open(p, "w", encoding="utf-8") as f:
                f.write(adaptive_xml)

    print(f"Generated {fg_count} adaptive foregrounds and {launcher_count} launcher icons (true PNG/WEBP).")


if __name__ == "__main__":
    main()
