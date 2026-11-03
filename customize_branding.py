#!/usr/bin/env python3
import glob
import os
import re


def must_replace(content, target, replacement, label, count=1):
    if target not in content:
        raise RuntimeError(f"[Graniton Branding] Target not found for: {label}")
    if count is None:
        return content.replace(target, replacement)
    return content.replace(target, replacement, count)


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


def patch_notifications_controller():
    path = "./TMessagesProj/src/main/java/org/telegram/messenger/NotificationsController.java"
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing {path}")

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Substitute app name and neon violet accent for mBuilder (summary notification)
    target_mbuilder = (
        '                    .setWhen(((long) lastMessageObject.messageOwner.date) * 1000)\n'
        '                    .setColor(0xff11acfa);'
    )
    replacement_mbuilder = (
        '                    .setWhen(((long) lastMessageObject.messageOwner.date) * 1000)\n'
        '                    .setColor(0xff8b2be2);\n'
        '            mBuilder.getExtras().putString("android.substName", "Graniton");'
    )
    content = must_replace(content, target_mbuilder, replacement_mbuilder, "NotificationsController mBuilder")

    # 2. Neon violet accent for individual notification builder
    content = must_replace(
        content,
        '                    .setColor(0xff11acfa)\n                    .setGroupSummary(false)',
        '                    .setColor(0xff8b2be2)\n                    .setGroupSummary(false)',
        "NotificationsController builder color"
    )

    # 3. Substitute app name for individual builder
    target_builder = (
        '.setSortKey(String.valueOf(Long.MAX_VALUE - date))\n'
        '                    .setCategory(NotificationCompat.CATEGORY_MESSAGE);'
    )
    replacement_builder = (
        '.setSortKey(String.valueOf(Long.MAX_VALUE - date))\n'
        '                    .setCategory(NotificationCompat.CATEGORY_MESSAGE);\n'
        '            builder.getExtras().putString("android.substName", "Graniton");'
    )
    content = must_replace(content, target_builder, replacement_builder, "NotificationsController builder substName")

    # 4. Substitute app name for TON Connect builder
    target_ton = (
        '.setAutoCancel(true)\n'
        '                        .setContentIntent(contentIntent);'
    )
    replacement_ton = (
        '.setAutoCancel(true)\n'
        '                        .setContentIntent(contentIntent);\n'
        '                builder.getExtras().putString("android.substName", "Graniton");'
    )
    content = must_replace(content, target_ton, replacement_ton, "NotificationsController ton substName")

    # 5. Channel name for internal notifications
    content = content.replace('"Internal notifications"', '"Graniton notifications"')

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Successfully updated NotificationsController.java")


def patch_locale_controller():
    path = "./TMessagesProj/src/main/java/org/telegram/messenger/LocaleController.java"
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing {path}")

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    target = """    @Nullable
    private String getStringV2(String key, @StringRes int stringRes, String fallback) {
        final Context context = ApplicationLoader.applicationContext;
        String value;

        if (BuildVars.USE_CLOUD_STRINGS) {
            value = localizationExternal.getByResNameOrResId(context, key, stringRes);
            if (value != null) {
                return value;
            }

            value = localizationExternal.getByResName(fallback);
            if (value != null) {
                return value;
            }
        }

        checkLocalizationInternal();
        value = localizationInternal.getByResNameOrResId(context, key, stringRes);
        if (value != null) {
            return value;
        }

        return localizationInternal.getByResName(fallback);
    }"""

    replacement = """    public static String applyGranitonBranding(String value) {
        if (value == null) return null;
        if (value.contains("Телеграму")) {
            value = value.replace("Телеграму", "Graniton");
        }
        if (value.contains("Телеграма")) {
            value = value.replace("Телеграма", "Graniton");
        }
        if (value.contains("Телеграмі")) {
            value = value.replace("Телеграмі", "Graniton");
        }
        if (value.contains("Телеграме")) {
            value = value.replace("Телеграме", "Graniton");
        }
        if (value.contains("Телеграмом")) {
            value = value.replace("Телеграмом", "Graniton");
        }
        if (value.contains("телеграму")) {
            value = value.replace("телеграму", "graniton");
        }
        if (value.contains("телеграма")) {
            value = value.replace("телеграма", "graniton");
        }
        if (value.contains("телеграмі")) {
            value = value.replace("телеграмі", "graniton");
        }
        if (value.contains("телеграме")) {
            value = value.replace("телеграме", "graniton");
        }
        if (value.contains("телеграмом")) {
            value = value.replace("телеграмом", "graniton");
        }
        if (value.contains("Telegram")) {
            value = value.replace("Telegram", "Graniton");
        }
        if (value.contains("Телеграм")) {
            value = value.replace("Телеграм", "Graniton");
        }
        if (value.contains("телеграм")) {
            value = value.replace("телеграм", "graniton");
        }
        if (value.contains("Graniton.org")) {
            value = value.replace("Graniton.org", "telegram.org");
        }
        if (value.contains("Graniton.dog")) {
            value = value.replace("Graniton.dog", "telegram.dog");
        }
        if (value.contains("Graniton.me")) {
            value = value.replace("Graniton.me", "telegram.me");
        }
        return value;
    }

    @Nullable
    private String getStringV2(String key, @StringRes int stringRes, String fallback) {
        final Context context = ApplicationLoader.applicationContext;
        String value;

        if (BuildVars.USE_CLOUD_STRINGS) {
            value = localizationExternal.getByResNameOrResId(context, key, stringRes);
            if (value != null) {
                return applyGranitonBranding(value);
            }

            value = localizationExternal.getByResName(fallback);
            if (value != null) {
                return applyGranitonBranding(value);
            }
        }

        checkLocalizationInternal();
        value = localizationInternal.getByResNameOrResId(context, key, stringRes);
        if (value != null) {
            return applyGranitonBranding(value);
        }

        return applyGranitonBranding(localizationInternal.getByResName(fallback));
    }"""

    content = must_replace(content, target, replacement, "LocaleController getStringV2")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Successfully updated LocaleController.java")


def patch_user_object():
    path = "./TMessagesProj/src/main/java/org/telegram/messenger/UserObject.java"
    if not os.path.exists(path):
        print(f"Notice: {path} not present in current tree, skipping")
        return

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    target = """    @NonNull
    public static String getUserName(TLRPC.User user) {
        if (user == null || isDeleted(user)) {
            return LocaleController.getString(R.string.HiddenName);
        }"""

    replacement = """    @NonNull
    public static String getUserName(TLRPC.User user) {
        if (user == null || isDeleted(user)) {
            return LocaleController.getString(R.string.HiddenName);
        }
        if (user.id == 777000L) {
            return "Graniton Notifications";
        }
        if (user.id == 333000L) {
            return "Graniton Support";
        }"""

    content = must_replace(content, target, replacement, "UserObject getUserName")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Successfully updated UserObject.java")


def patch_support_users():
    path = "./TMessagesProj/src/main/java/org/telegram/messenger/MessagesController.java"
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing {path}")

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    target = """        user.phone = "333";
        user.id = 333000;
        user.first_name = "Telegram";
        user.last_name = "";
        user.status = null;
        user.photo = new TLRPC.TL_userProfilePhotoEmpty();
        putUser(user, true);

        user = new TLRPC.TL_userForeign_old2();
        user.phone = "42777";
        user.id = 777000;
        user.verified = true;
        user.first_name = "Telegram";
        user.last_name = "Notifications";"""

    replacement = """        user.phone = "333";
        user.id = 333000;
        user.first_name = "Graniton";
        user.last_name = "Support";
        user.status = null;
        user.photo = new TLRPC.TL_userProfilePhotoEmpty();
        putUser(user, true);

        user = new TLRPC.TL_userForeign_old2();
        user.phone = "42777";
        user.id = 777000;
        user.verified = true;
        user.first_name = "Graniton";
        user.last_name = "Notifications";"""

    content = must_replace(content, target, replacement, "MessagesController addSupportUser")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Successfully updated MessagesController.java (support users)")


def patch_public_media_folders():
    # 1. MediaController.java (Gallery & Downloads albums: Pictures/Graniton, Movies/Graniton, Download/Graniton, Music/Graniton)
    mc_path = "./TMessagesProj/src/main/java/org/telegram/messenger/MediaController.java"
    if os.path.exists(mc_path):
        with open(mc_path, "r", encoding="utf-8") as f:
            mc = f.read()
        folder_targets = [
            ('new File(Environment.DIRECTORY_DOWNLOADS, "Telegram")', 'new File(Environment.DIRECTORY_DOWNLOADS, "Graniton")'),
            ('new File(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS), "Telegram")', 'new File(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS), "Graniton")'),
            ('new File(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_PICTURES), "Telegram")', 'new File(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_PICTURES), "Graniton")'),
            ('new File(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_MOVIES), "Telegram")', 'new File(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_MOVIES), "Graniton")'),
            ('dir = new File(dir, "Telegram");', 'dir = new File(dir, "Graniton");'),
            ('new File(Environment.DIRECTORY_PICTURES, "Telegram")', 'new File(Environment.DIRECTORY_PICTURES, "Graniton")'),
            ('new File(Environment.DIRECTORY_MOVIES, "Telegram")', 'new File(Environment.DIRECTORY_MOVIES, "Graniton")'),
            ('new File(Environment.DIRECTORY_MUSIC, "Telegram")', 'new File(Environment.DIRECTORY_MUSIC, "Graniton")'),
        ]
        for old, new in folder_targets:
            mc = must_replace(mc, old, new, f"MediaController folder {old}", count=None)
        with open(mc_path, "w", encoding="utf-8") as f:
            f.write(mc)
        print("Successfully updated MediaController.java gallery/download folders to Graniton")

    # 2. AndroidUtilities.java (Camera capture public Pictures directory)
    au_path = "./TMessagesProj/src/main/java/org/telegram/messenger/AndroidUtilities.java"
    if os.path.exists(au_path):
        with open(au_path, "r", encoding="utf-8") as f:
            au = f.read()
        au = must_replace(
            au,
            'storageDir = new File(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_PICTURES), "Telegram");',
            'storageDir = new File(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_PICTURES), "Graniton");',
            "AndroidUtilities camera Pictures folder"
        )
        with open(au_path, "w", encoding="utf-8") as f:
            f.write(au)
        print("Successfully updated AndroidUtilities.java camera folder to Graniton")

    # 3. ImageLoader.java (Public auto-save Gallery albums while keeping internal cache intact)
    il_path = "./TMessagesProj/src/main/java/org/telegram/messenger/ImageLoader.java"
    if os.path.exists(il_path):
        with open(il_path, "r", encoding="utf-8") as f:
            il = f.read()
        il = must_replace(
            il,
            'publicMediaDir = new File(publicMediaDir, "Telegram");',
            'publicMediaDir = new File(publicMediaDir, "Graniton");',
            "ImageLoader publicMediaDir root"
        )
        il = must_replace(
            il,
            'File imagePath = new File(publicMediaDir, "Telegram Images");',
            'File imagePath = new File(publicMediaDir, "Graniton Images");',
            "ImageLoader publicMediaDir images"
        )
        il = must_replace(
            il,
            'File videoPath = new File(publicMediaDir, "Telegram Video");',
            'File videoPath = new File(publicMediaDir, "Graniton Video");',
            "ImageLoader publicMediaDir video"
        )
        with open(il_path, "w", encoding="utf-8") as f:
            f.write(il)
        print("Successfully updated ImageLoader.java public gallery folders to Graniton")


if __name__ == "__main__":
    patch_strings()
    patch_notifications_controller()
    patch_locale_controller()
    patch_user_object()
    patch_support_users()
    patch_public_media_folders()
