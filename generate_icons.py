#!/usr/bin/env python3
import os
import sys

def main():
    if not os.path.exists("logo.png"):
        print("logo.png not found, skipping icon generation")
        return

    # 1. Attempt to use PIL/Pillow for high-quality adaptive icon scaling
    has_pil = False
    try:
        from PIL import Image
        has_pil = True
    except ImportError:
        print("PIL not found, attempting to install pillow...")
        import subprocess
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "--break-system-packages", "pillow"], check=True)
            from PIL import Image
            has_pil = True
        except Exception as e:
            print(f"Could not install Pillow: {e}. Falling back to direct file copy.")

    foreground_path = "logo.png"

    if has_pil:
        try:
            with open("logo.png", "rb") as f:
                data = f.read()

            try:
                img = Image.open("logo.png")
            except Exception:
                import io
                img = Image.open(io.BytesIO(data[:33] + data[366:]))

            img = img.convert("RGBA")

            # Adaptive icon foreground (512x512 with safe margin ~72%)
            target_size = 512
            canvas = Image.new("RGBA", (target_size, target_size), (0, 0, 0, 0))
            scale = min(368 / img.width, 368 / img.height)
            new_w = max(1, int(img.width * scale))
            new_h = max(1, int(img.height * scale))
            resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            pos_x = (target_size - new_w) // 2
            pos_y = (target_size - new_h) // 2
            canvas.paste(resized, (pos_x, pos_y), resized)
            canvas.save("icon_foreground_gen.png", "PNG")
            foreground_path = "icon_foreground_gen.png"
            print("Successfully generated icon_foreground_gen.png with safe margins.")
        except Exception as e:
            print(f"Error during Pillow processing: {e}. Using raw logo.png.")
            foreground_path = "logo.png"

    # 2. Overwrite all foreground and launcher icons across all res folders
    res_dir = "./TMessagesProj/src/main/res"
    if os.path.exists(res_dir):
        with open(foreground_path, "rb") as f:
            fg_bytes = f.read()
        with open("logo.png", "rb") as f:
            logo_bytes = f.read()

        for root, dirs, files in os.walk(res_dir):
            for file in files:
                full_path = os.path.join(root, file)
                if file.startswith("icon_foreground") and file.endswith(".png"):
                    with open(full_path, "wb") as dst:
                        dst.write(fg_bytes)
                elif file.startswith("ic_launcher") and (file.endswith(".png") or file.endswith(".webp")):
                    with open(full_path, "wb") as dst:
                        dst.write(logo_bytes)

        # 3. Write Dark Purple background XML (#0d0214)
        bg_xml = '<?xml version="1.0" encoding="utf-8"?>\n<shape xmlns:android="http://schemas.android.com/apk/res/android">\n    <solid android:color="#0d0214" />\n</shape>\n'
        for bg_file in ["icon_background.xml", "icon_background_sa.xml"]:
            p = os.path.join(res_dir, "drawable", bg_file)
            if os.path.exists(os.path.dirname(p)):
                with open(p, "w") as f:
                    f.write(bg_xml)

        # 4. Write clean adaptive icon XML (without monochrome paper plane)
        adaptive_xml = '<?xml version="1.0" encoding="utf-8"?>\n<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">\n    <background android:drawable="@drawable/icon_background" />\n    <foreground android:drawable="@mipmap/icon_foreground" />\n</adaptive-icon>\n'
        for icon_file in ["ic_launcher.xml", "ic_launcher_round.xml"]:
            p = os.path.join(res_dir, "mipmap-anydpi-v26", icon_file)
            if os.path.exists(os.path.dirname(p)):
                with open(p, "w") as f:
                    f.write(adaptive_xml)

    print("All adaptive icons, legacy icons, and background XMLs updated successfully!")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Warning: Icon customization encountered error: {e}")
