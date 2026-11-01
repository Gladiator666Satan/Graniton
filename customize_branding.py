#!/usr/bin/env python3
import os
import glob
import re

def patch_strings():
    res_dir = "./TMessagesProj/src/main/res"
    if not os.path.exists(res_dir):
        print(f"Directory {res_dir} not found")
        return

    string_files = glob.glob(os.path.join(res_dir, "values*", "strings.xml"), recursive=True)
    print(f"Found {len(string_files)} strings.xml files.")

    direct_replacements = {
        'AppName': 'Graniton',
        'AppNameBeta': 'Graniton Beta',
        'NotificationHiddenName': 'Graniton',
        'NotificationHiddenChatName': 'Graniton',
        'SecretChatName': 'Graniton',
        'Page1Title': 'Graniton',
        'MapPreviewProviderTelegram': 'Graniton',
        'AppLocked': 'Graniton Locked',
        'VoipInCallBranding': 'Graniton Call',
        'VoipInVideoCallBranding': 'Graniton Video Call',
        'VoipInConferenceCallBranding': 'Graniton Group Call',
        'CallViaTelegram': 'Graniton Call',
        'VideoCallViaTelegram': 'Graniton Video Call',
        'VoiceCallViaTelegram': 'Graniton Voice Call',
        'EnterYourTelegramPasscode': 'Enter your Graniton passcode',
        'TelegramVersion': 'Graniton for Android %1$s',
        'AppUpdate': 'Update Graniton',
        'AppUpdateBeta': 'Update Graniton Beta',
        'UpdateTelegram': 'Update Graniton',
        'ClearTelegramCache': 'Clear Graniton Cache',
        'UnlockToUse': 'Unlock to use Graniton',
        'NoChats': 'Welcome to Graniton'
    }

    for file_path in string_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            modified = False
            for key, new_val in direct_replacements.items():
                pattern = re.compile(rf'<string name="{key}">.*?</string>')
                if pattern.search(content):
                    new_content = pattern.sub(f'<string name="{key}">{new_val}</string>', content)
                    if new_content != content:
                        content = new_content
                        modified = True

            if modified:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"Updated: {file_path}")
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

def patch_notifications_controller():
    path = "./TMessagesProj/src/main/java/org/telegram/messenger/NotificationsController.java"
    if not os.path.exists(path):
        print(f"File {path} not found")
        return

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Substitute app name for mBuilder (summary notification)
    target_mbuilder = (
        '                    .setWhen(((long) lastMessageObject.messageOwner.date) * 1000)\n'
        '                    .setColor(0xff11acfa);'
    )
    replacement_mbuilder = (
        '                    .setWhen(((long) lastMessageObject.messageOwner.date) * 1000)\n'
        '                    .setColor(0xff11acfa);\n'
        '            mBuilder.getExtras().putString("android.substName", "Graniton");'
    )
    if target_mbuilder in content:
        content = content.replace(target_mbuilder, replacement_mbuilder, 1)
        print("Patched mBuilder in NotificationsController.java")
    else:
        print("WARNING: target_mbuilder not found in NotificationsController.java")

    # 2. Substitute app name for individual builder
    target_builder = (
        '.setSortKey(String.valueOf(Long.MAX_VALUE - date))\n'
        '                    .setCategory(NotificationCompat.CATEGORY_MESSAGE);'
    )
    replacement_builder = (
        '.setSortKey(String.valueOf(Long.MAX_VALUE - date))\n'
        '                    .setCategory(NotificationCompat.CATEGORY_MESSAGE);\n'
        '            builder.getExtras().putString("android.substName", "Graniton");'
    )
    if target_builder in content:
        content = content.replace(target_builder, replacement_builder, 1)
        print("Patched builder in NotificationsController.java")
    else:
        print("WARNING: target_builder not found in NotificationsController.java")

    # 3. Substitute app name for TON Connect builder
    target_ton = (
        '.setAutoCancel(true)\n'
        '                        .setContentIntent(contentIntent);'
    )
    replacement_ton = (
        '.setAutoCancel(true)\n'
        '                        .setContentIntent(contentIntent);\n'
        '                builder.getExtras().putString("android.substName", "Graniton");'
    )
    if target_ton in content:
        content = content.replace(target_ton, replacement_ton, 1)
        print("Patched ton builder in NotificationsController.java")
    else:
        print("WARNING: target_ton not found in NotificationsController.java")

    # 4. Channel name for internal notifications
    content = content.replace('"Internal notifications"', '"Graniton notifications"')

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Successfully updated NotificationsController.java")

if __name__ == "__main__":
    patch_strings()
    patch_notifications_controller()
