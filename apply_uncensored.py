#!/usr/bin/env python3
"""
Graniton Uncensored Edition Mod Script (Full Freedom Branch)
- Bypasses Google Play Store ("android", "android-all") & cross-platform ("all") channel/bot/message restrictions
  ("This channel cannot be displayed because it cannot be viewed in Telegram apps downloaded from Google Play")
- Unlocks 18+ / Sensitive Content globally without forced media blur or popup warnings
  (while preserving normal user-sent media spoilers!)
- Bypasses Telegram v13.1+ video-selfie age verification bot gate (ThemeActivity.verifyAge)
- Strips Google Play Store installer identifier ("com.android.vending") from MTProto initConnection
  while preserving real packageId & SHA-256 certificate for Play Integrity & Firebase Push compatibility
"""
import os


def must_replace(content, target, replacement, label, count=1):
    if target not in content:
        raise RuntimeError(f"[Graniton Uncensored] Target not found for: {label}")
    if count is None:
        return content.replace(target, replacement)
    return content.replace(target, replacement, count)


def patch_messages_controller():
    path = "./TMessagesProj/src/main/java/org/telegram/messenger/MessagesController.java"
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing {path}")

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Bypass all client-side channel, bot, mini-app, message, and PhotoViewer restriction_reason blocks
    old_restriction = (
        "    public String getRestrictionReason(ArrayList<TLRPC.RestrictionReason> reasons) {\n"
        "        if (reasons.isEmpty()) {\n"
        "            return null;\n"
        "        }"
    )
    new_restriction = (
        "    public String getRestrictionReason(ArrayList<TLRPC.RestrictionReason> reasons) {\n"
        "        if (true) {\n"
        "            return null; // Graniton Uncensored: bypass Google Play & platform restriction_reason blocks\n"
        "        }\n"
        "        if (reasons.isEmpty()) {\n"
        "            return null;\n"
        "        }"
    )
    content = must_replace(content, old_restriction, new_restriction, "MessagesController.getRestrictionReason")

    # 2. Bypass checkSensitive channel/bot entry gates
    old_is_sensitive = (
        "    public boolean isSensitive(ArrayList<TLRPC.RestrictionReason> reasons) {\n"
        "        if (reasons == null || reasons.isEmpty()) {\n"
        "            return false;\n"
        "        }"
    )
    new_is_sensitive = (
        "    public boolean isSensitive(ArrayList<TLRPC.RestrictionReason> reasons) {\n"
        "        if (true) {\n"
        "            return false; // Graniton Uncensored: disable sensitive channel gates\n"
        "        }\n"
        "        if (reasons == null || reasons.isEmpty()) {\n"
        "            return false;\n"
        "        }"
    )
    content = must_replace(content, old_is_sensitive, new_is_sensitive, "MessagesController.isSensitive")

    # 3. Globally enable sensitive content display
    old_show_sensitive = (
        "    public boolean showSensitiveContent() {\n"
        "        if (contentSettings != null && System.currentTimeMillis() - contentSettingsLoadedTime < 1000 * 60 * 60) {\n"
        "            return contentSettings.sensitive_enabled;\n"
        "        }"
    )
    new_show_sensitive = (
        "    public boolean showSensitiveContent() {\n"
        "        if (true) {\n"
        "            return true; // Graniton Uncensored: always show sensitive content\n"
        "        }\n"
        "        if (contentSettings != null && System.currentTimeMillis() - contentSettingsLoadedTime < 1000 * 60 * 60) {\n"
        "            return contentSettings.sensitive_enabled;\n"
        "        }"
    )
    content = must_replace(content, old_show_sensitive, new_show_sensitive, "MessagesController.showSensitiveContent")

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Successfully patched MessagesController.java (Uncensored channel & content access)")


def patch_message_object():
    path = "./TMessagesProj/src/main/java/org/telegram/messenger/MessageObject.java"
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing {path}")

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Disable forced "Sensitive Content" blur on individual messages while keeping user-sent media.spoiler intact
    old_msg_sensitive = (
        "    public Boolean isSensitiveCached;\n"
        "    public boolean isSensitive() {\n"
        "        if (isSensitiveCached != null) return isSensitiveCached;"
    )
    new_msg_sensitive = (
        "    public Boolean isSensitiveCached;\n"
        "    public boolean isSensitive() {\n"
        "        if (true) return isSensitiveCached = false; // Graniton Uncensored: never censor sensitive media\n"
        "        if (isSensitiveCached != null) return isSensitiveCached;"
    )
    content = must_replace(content, old_msg_sensitive, new_msg_sensitive, "MessageObject.isSensitive")

    old_hidden_sensitive = (
        "    public boolean isHiddenSensitive() {\n"
        "        return isSensitive() && !MessagesController.getInstance(currentAccount).showSensitiveContent();\n"
        "    }"
    )
    new_hidden_sensitive = (
        "    public boolean isHiddenSensitive() {\n"
        "        return false; // Graniton Uncensored: never hide sensitive media\n"
        "    }"
    )
    content = must_replace(content, old_hidden_sensitive, new_hidden_sensitive, "MessageObject.isHiddenSensitive")

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Successfully patched MessageObject.java (Uncensored media rendering)")


def patch_theme_activity():
    path = "./TMessagesProj/src/main/java/org/telegram/ui/ThemeActivity.java"
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing {path}")

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    old_verify = (
        "    public static void verifyAge(Context context, int currentAccount, Utilities.Callback<Boolean> done, Theme.ResourcesProvider resourcesProvider) {\n"
        "        final MessagesController messagesController = MessagesController.getInstance(currentAccount);"
    )
    new_verify = (
        "    public static void verifyAge(Context context, int currentAccount, Utilities.Callback<Boolean> done, Theme.ResourcesProvider resourcesProvider) {\n"
        "        if (true) {\n"
        "            if (done != null) {\n"
        "                done.run(true);\n"
        "            }\n"
        "            return; // Graniton Uncensored: bypass video age verification bot gate\n"
        "        }\n"
        "        final MessagesController messagesController = MessagesController.getInstance(currentAccount);"
    )
    content = must_replace(content, old_verify, new_verify, "ThemeActivity.verifyAge")

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Successfully patched ThemeActivity.java (Bypassed video age verification gate)")


def patch_connections_manager_and_build_vars():
    cm_path = "./TMessagesProj/src/main/java/org/telegram/tgnet/ConnectionsManager.java"
    if not os.path.exists(cm_path):
        raise FileNotFoundError(f"Missing {cm_path}")

    with open(cm_path, "r", encoding="utf-8") as f:
        cm = f.read()

    old_init = (
        '        if (installer == null) {\n'
        '            installer = "";\n'
        '        }\n'
        '        String packageId = "";'
    )
    new_init = (
        '        installer = ""; // Graniton Uncensored: Direct/Standalone mode (never report Play Store installer)\n'
        '        String packageId = "";'
    )
    cm = must_replace(cm, old_init, new_init, "ConnectionsManager.init direct installer")

    with open(cm_path, "w", encoding="utf-8") as f:
        f.write(cm)
    print("Successfully patched ConnectionsManager.java (Direct non-store MTProto installer)")

    bv_path = "./TMessagesProj/src/main/java/org/telegram/messenger/BuildVars.java"
    if not os.path.exists(bv_path):
        raise FileNotFoundError(f"Missing {bv_path}")

    with open(bv_path, "r", encoding="utf-8") as f:
        bv = f.read()

    bv = must_replace(
        bv,
        "public static boolean CHECK_UPDATES = true;",
        "public static boolean CHECK_UPDATES = false;",
        "BuildVars.CHECK_UPDATES = false"
    )

    with open(bv_path, "w", encoding="utf-8") as f:
        f.write(bv)
    print("Successfully patched BuildVars.java (Disabled upstream store/standalone update checks)")


if __name__ == "__main__":
    print("=== Applying Graniton Uncensored Edition Patches ===")
    patch_messages_controller()
    patch_message_object()
    patch_theme_activity()
    patch_connections_manager_and_build_vars()
    print("=== Graniton Uncensored Edition Applied Successfully ===")
