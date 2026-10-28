#!/usr/bin/env python3
import os
import glob

def hex_to_int(h):
    h = h.lstrip('#')
    if len(h) == 6:
        h = 'FF' + h
    val = int(h, 16)
    if val >= 0x80000000:
        val -= 0x100000000
    return val

def update_attheme_files():
    assets_dir = "./TMessagesProj/src/main/assets"
    if not os.path.exists(assets_dir):
        print(f"Assets dir {assets_dir} not found")
        return

    # Graniton Dark Violet Synergy Palette
    replacements = {
        'windowBackgroundWhite': hex_to_int('FF0D0214'),          # #0d0214 Deep obsidian
        'windowBackgroundGray': hex_to_int('FF08000C'),           # #08000c Contrast
        'dialogBackground': hex_to_int('FF180B2B'),               # #180b2b Elevated card
        'dialogBackgroundGray': hex_to_int('FF10051E'),
        'actionBarDefault': hex_to_int('FF160926'),               # #160926 Elevated bar
        'actionBarDefaultArchived': hex_to_int('FF160926'),
        'actionBarActionModeDefault': hex_to_int('FF1F0E35'),
        'actionBarDefaultSubmenuBackground': hex_to_int('FF1F0E35'),
        'actionBarDefaultTitle': hex_to_int('FFFFFFFF'),
        'actionBarDefaultIcon': hex_to_int('FFA855F7'),
        'chat_topPanelBackground': hex_to_int('FF160926'),
        'chat_messagePanelBackground': hex_to_int('FF160926'),
        'chat_emojiPanelBackground': hex_to_int('FF160926'),
        'chat_wallpaper': hex_to_int('FF0D0214'),
        'chat_inBubble': hex_to_int('FF231238'),                  # #231238 Deep plum
        'chat_inBubbleSelected': hex_to_int('FF341A52'),
        'chat_outBubble': hex_to_int('FF7928CA'),                 # #7928ca Electric violet
        'chat_outBubbleSelected': hex_to_int('FFA855F7'),
        'chat_outBubbleGradient': hex_to_int('FF9333EA'),         # #9333ea Gradient
        'chat_messageTextIn': hex_to_int('FFF3EEF8'),
        'chat_messageTextOut': hex_to_int('FFFFFFFF'),
        'chat_messageLinkIn': hex_to_int('FFC084FC'),
        'chat_messageLinkOut': hex_to_int('FFE9D5FF'),            # Readable link distinct from text
        'chats_actionBackground': hex_to_int('FF8B2BE2'),         # #8b2be2 Neon FAB
        'chats_actionPressedBackground': hex_to_int('FF741ECC'),
        'chats_unreadCounter': hex_to_int('FF8B2BE2'),
        'windowBackgroundWhiteBlueText': hex_to_int('FF8B2BE2'),
        'windowBackgroundWhiteBlueText2': hex_to_int('FF8B2BE2'),
        'windowBackgroundWhiteBlueText4': hex_to_int('FF8B2BE2'),
        'windowBackgroundWhiteBlueHeader': hex_to_int('FFA855F7'),
        'dialogButton': hex_to_int('FF8B2BE2'),
        'dialogTextBlue': hex_to_int('FF8B2BE2'),
        'switchTrackBlueChecked': hex_to_int('FF8B2BE2'),
        'featuredStickers_addButton': hex_to_int('FF8B2BE2'),
        'player_buttonActive': hex_to_int('FF8B2BE2'),
        'chat_inVoiceSeekbarFill': hex_to_int('FF8B2BE2'),
        'chats_nameMessage': -1,
        'chats_menuTopBackgroundCats': hex_to_int('FF08000C'),
        'telegram_color_dialogsLogo': hex_to_int('FFFFFFFF')
    }

    attheme_files = glob.glob(os.path.join(assets_dir, "*.attheme"))
    print(f"Found {len(attheme_files)} .attheme files in {assets_dir}")
    for file_path in attheme_files:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            lines = content.splitlines()
            new_lines = []
            existing_keys = set()
            for line in lines:
                if "=" in line:
                    key, val = line.split("=", 1)
                    existing_keys.add(key)
                    if key in replacements:
                        new_lines.append(f"{key}={replacements[key]}")
                        continue
                new_lines.append(line)

            # Add missing crucial keys
            for k, v in replacements.items():
                if k not in existing_keys:
                    new_lines.append(f"{k}={v}")

            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(new_lines) + "\n")
            print(f"Updated {os.path.basename(file_path)} with Dark Violet palette.")
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
        ("public static final int TELEGRAM_COLOR = 0xFF229AF0;", "public static final int TELEGRAM_COLOR = 0xFF8B2BE2;"),
        ("public static final int TELEGRAM_COLOR_TEXT = 0xFF298ACF;", "public static final int TELEGRAM_COLOR_TEXT = 0xFF8B2BE2;"),
        ("defaultColors[key_windowBackgroundWhite] = 0xffffffff;", "defaultColors[key_windowBackgroundWhite] = 0xff0d0214;"),
        ("defaultColors[key_windowBackgroundGray] = 0xffF1F1F3;", "defaultColors[key_windowBackgroundGray] = 0xff08000c;"),
        ("defaultColors[key_actionBarDefault] = 0xffffffff;", "defaultColors[key_actionBarDefault] = 0xff160926;"),
        ("defaultColors[key_chats_actionBackground] = 0xff65a9e0;", "defaultColors[key_chats_actionBackground] = 0xff8b2be2;"),
        ("defaultColors[key_windowBackgroundWhiteBlackText] = DEFAULT_BLACK_TEXT;", "defaultColors[key_windowBackgroundWhiteBlackText] = 0xffffffff;"),
        ("defaultColors[key_actionBarDefaultTitle] = DEFAULT_BLACK_TEXT;", "defaultColors[key_actionBarDefaultTitle] = 0xffffffff;"),
        ("defaultColors[key_actionBarDefaultIcon] = DEFAULT_BLACK_TEXT;", "defaultColors[key_actionBarDefaultIcon] = 0xffa855f7;"),
        ("defaultColors[key_windowBackgroundWhiteGrayText] = 0xff808384;", "defaultColors[key_windowBackgroundWhiteGrayText] = 0xff9e91b2;")
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
    print("=== Applying Graniton Dark Violet Theme ===")
    update_attheme_files()
    update_theme_colors_java()
    update_theme_java()
    print("=== Graniton Dark Violet Theme applied successfully! ===")

if __name__ == "__main__":
    main()
