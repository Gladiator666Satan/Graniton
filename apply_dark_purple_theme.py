#!/usr/bin/env python3
import os
import glob

def update_attheme_files():
    assets_dir = "./TMessagesProj/src/main/assets"
    if not os.path.exists(assets_dir):
        print(f"Assets dir {assets_dir} not found")
        return

    # Dark Purple Energy Palette
    # Main Background: #0d0214 (-15924716)
    # Elevated Cards / Headers: #1a0b2e (-15070418)
    # Darkest contrast: #08000c (-16252916)
    # BlueViolet Neon Accent: #8a2be2 (-7722014)
    # Secondary Violet: #a855f7 (-5745161)
    # Bubble Surface: #25113d (-14347963)
    replacements = {
        'windowBackgroundWhite': -15924716,          # #0d0214
        'windowBackgroundGray': -16252916,           # #08000c
        'dialogBackground': -15070418,               # #1a0b2e
        'dialogBackgroundGray': -15924716,           # #0d0214
        'actionBarDefault': -15070418,               # #1a0b2e
        'actionBarDefaultArchived': -15070418,
        'actionBarActionModeDefault': -15070418,
        'actionBarDefaultSubmenuBackground': -15070418,
        'chat_topPanelBackground': -15070418,
        'chat_messagePanelBackground': -15070418,
        'chat_emojiPanelBackground': -15070418,
        'chat_wallpaper': -15924716,                 # #0d0214
        'chat_inBubble': -14347963,                  # #25113d
        'chat_inBubbleSelected': -13692080,          # #2f174e
        'chat_outBubble': -7722014,                  # #8a2be2
        'chat_outBubbleSelected': -6737938,          # #9932ee
        'chat_outBubbleGradient': -5745161,          # #a855f7
        'chats_actionBackground': -7722014,          # #8a2be2
        'chats_actionPressedBackground': -8840248,   # #791fc8
        'chats_unreadCounter': -7722014,             # #8a2be2
        'windowBackgroundWhiteBlueText': -7722014,   # #8a2be2
        'windowBackgroundWhiteBlueText2': -7722014,
        'windowBackgroundWhiteBlueText4': -7722014,
        'windowBackgroundWhiteBlueHeader': -5745161, # #a855f7
        'dialogButton': -7722014,                    # #8a2be2
        'dialogTextBlue': -7722014,
        'switchTrackBlueChecked': -7722014,
        'featuredStickers_addButton': -7722014,
        'player_buttonActive': -7722014,
        'chat_inVoiceSeekbarFill': -7722014,
        'chats_nameMessage': -1,                     # white message text in list
        'chats_menuTopBackgroundCats': -16252916     # #08000c
    }

    attheme_files = glob.glob(os.path.join(assets_dir, "*.attheme"))
    print(f"Found {len(attheme_files)} .attheme files in {assets_dir}")
    for file_path in attheme_files:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            lines = content.splitlines()
            new_lines = []
            for line in lines:
                if "=" in line:
                    key, val = line.split("=", 1)
                    if key in replacements:
                        new_lines.append(f"{key}={replacements[key]}")
                        continue
                new_lines.append(line)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(new_lines) + "\n")
            print(f"Updated {os.path.basename(file_path)} with Dark Purple Energy palette.")
        except Exception as e:
            print(f"Error updating {file_path}: {e}")

def update_theme_colors_java():
    path = "./TMessagesProj/src/main/java/org/telegram/ui/ActionBar/ThemeColors.java"
    if not os.path.exists(path):
        print(f"{path} not found")
        return

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    replacements = [
        ("public static final int TELEGRAM_COLOR = 0xFF229AF0;", "public static final int TELEGRAM_COLOR = 0xFF8A2BE2;"),
        ("public static final int TELEGRAM_COLOR_TEXT = 0xFF298ACF;", "public static final int TELEGRAM_COLOR_TEXT = 0xFF8A2BE2;"),
        ("defaultColors[key_windowBackgroundWhite] = 0xffffffff;", "defaultColors[key_windowBackgroundWhite] = 0xff0d0214;"),
        ("defaultColors[key_windowBackgroundGray] = 0xffF1F1F3;", "defaultColors[key_windowBackgroundGray] = 0xff08000c;"),
        ("defaultColors[key_actionBarDefault] = 0xffffffff;", "defaultColors[key_actionBarDefault] = 0xff1a0b2e;"),
        ("defaultColors[key_chats_actionBackground] = 0xff65a9e0;", "defaultColors[key_chats_actionBackground] = 0xff8a2be2;"),
        ("defaultColors[key_windowBackgroundWhiteBlackText] = DEFAULT_BLACK_TEXT;", "defaultColors[key_windowBackgroundWhiteBlackText] = 0xffffffff;"),
        ("defaultColors[key_actionBarDefaultTitle] = DEFAULT_BLACK_TEXT;", "defaultColors[key_actionBarDefaultTitle] = 0xffffffff;"),
        ("defaultColors[key_actionBarDefaultIcon] = DEFAULT_BLACK_TEXT;", "defaultColors[key_actionBarDefaultIcon] = 0xffffffff;"),
        ("defaultColors[key_windowBackgroundWhiteGrayText] = 0xff808384;", "defaultColors[key_windowBackgroundWhiteGrayText] = 0xffa094b8;")
    ]

    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
        else:
            print(f"Notice: pattern not found in ThemeColors.java: {old[:40]}")

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Updated ThemeColors.java successfully.")

def update_theme_java():
    path = "./TMessagesProj/src/main/java/org/telegram/ui/ActionBar/Theme.java"
    if not os.path.exists(path):
        print(f"{path} not found")
        return

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Force applyingTheme to default to currentNightTheme on fresh launch
    old_apply = "if (applyingTheme == null) {\n            applyingTheme = defaultTheme;\n        }"
    new_apply = "if (applyingTheme == null) {\n            applyingTheme = currentNightTheme != null ? currentNightTheme : defaultTheme;\n        }"
    if old_apply in content:
        content = content.replace(old_apply, new_apply)
    else:
        content = content.replace("applyingTheme = defaultTheme;", "applyingTheme = currentNightTheme != null ? currentNightTheme : defaultTheme;")

    # 2. Disable switching to light theme on AUTO_NIGHT_TYPE_SYSTEM if system is light
    old_night = 'selectedAutoNightType = preferences.getInt("selectedAutoNightType", Build.VERSION.SDK_INT >= 29 ? AUTO_NIGHT_TYPE_SYSTEM : AUTO_NIGHT_TYPE_NONE);'
    new_night = 'selectedAutoNightType = preferences.getInt("selectedAutoNightType", AUTO_NIGHT_TYPE_NONE);'
    if old_night in content:
        content = content.replace(old_night, new_night)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Updated Theme.java successfully.")

def main():
    print("=== Applying Dark Purple Energy Theme to Graniton ===")
    update_attheme_files()
    update_theme_colors_java()
    update_theme_java()
    print("=== Dark Purple Energy Theme applied successfully! ===")

if __name__ == "__main__":
    main()
