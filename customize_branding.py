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

def patch_locale_controller():
    path = "./TMessagesProj/src/main/java/org/telegram/messenger/LocaleController.java"
    if not os.path.exists(path):
        print(f"File {path} not found")
        return

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

    if target in content:
        content = content.replace(target, replacement, 1)
        print("Patched LocaleController.java (dynamic Graniton UI branding with inflections)")
    else:
        print("WARNING: target not found in LocaleController.java")

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Successfully updated LocaleController.java")

def patch_user_object():
    path = "./TMessagesProj/src/main/java/org/telegram/messenger/UserObject.java"
    if not os.path.exists(path):
        print(f"File {path} not found")
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

    if target in content:
        content = content.replace(target, replacement, 1)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print("Patched UserObject.java (Graniton system user branding)")
    else:
        print("WARNING: target not found in UserObject.java")

def patch_support_users():
    path = "./TMessagesProj/src/main/java/org/telegram/messenger/MessagesController.java"
    if not os.path.exists(path):
        print(f"File {path} not found")
        return

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

    if target in content:
        content = content.replace(target, replacement, 1)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print("Patched MessagesController.java (addSupportUser Graniton branding)")
    else:
        print("WARNING: target not found in MessagesController.java for addSupportUser")

if __name__ == "__main__":
    patch_strings()
    patch_notifications_controller()
    patch_locale_controller()
    patch_user_object()
    patch_support_users()
