#!/usr/bin/env python3
"""
Graniton Power-Pack Mod Script
- HD 60fps Round Video Notes (720p @ 60fps + 4.5Mbps bitrate)
- True Ghost Mode (Disable typing, recording audio/video status)
- Anti-Delete Protection (Ignore incoming remote message deletions)
- Bypass Restricted Content (Save media and copy from noforwards channels)
- Client-Side Premium Unlock (Voice-to-Text UI, real-time chat translation, no-ads)
- Force 120Hz Smooth Motion on Galaxy S26 Ultra
"""
import os
import re

def patch_instant_camera_hd():
    path = "./TMessagesProj/src/main/java/org/telegram/ui/Components/InstantCameraView.java"
    if not os.path.exists(path):
        print(f"File {path} not found")
        return

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Boost frame rate to 60fps
    if "private static final int FRAME_RATE = 30;" in content:
        content = content.replace("private static final int FRAME_RATE = 30;", "private static final int FRAME_RATE = 60;", 1)
        print("InstantCameraView: Set FRAME_RATE = 60")

    # 2. Boost resolution to 720p and bitrate to 4.5Mbps
    old_res = '''            int resolution = MessagesController.getInstance(currentAccount).roundVideoSize;
            int bitrate = MessagesController.getInstance(currentAccount).roundVideoBitrate * 1024;'''
    new_res = '''            int resolution = 720; // Graniton HD Round Video (720x720)
            int bitrate = 4500000; // 4.5 Mbps Studio Bitrate'''
    if old_res in content:
        content = content.replace(old_res, new_res, 1)
        print("InstantCameraView: Boosted resolution to 720p & bitrate to 4.5Mbps")

    # 3. Boost videoEditedInfo result dimensions
    content = content.replace("videoEditedInfo.resultWidth = videoEditedInfo.originalWidth = 360;", "videoEditedInfo.resultWidth = videoEditedInfo.originalWidth = 720;")
    content = content.replace("videoEditedInfo.resultHeight = videoEditedInfo.originalHeight = 360;", "videoEditedInfo.resultHeight = videoEditedInfo.originalHeight = 720;")
    content = content.replace("videoEditedInfo.bitrate = 1000000;", "videoEditedInfo.bitrate = 4500000;")

    # 4. Always allow big size camera
    content = content.replace(
        "private boolean allowBigSizeCamera() {",
        "private boolean allowBigSizeCamera() { return true; } private boolean _unused_allowBigSizeCamera() {",
        1
    )

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Successfully patched InstantCameraView.java")

def patch_ghost_and_anti_delete():
    path = "./TMessagesProj/src/main/java/org/telegram/messenger/MessagesController.java"
    if not os.path.exists(path):
        print(f"File {path} not found")
        return

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. True Ghost Mode: Disable sending typing status
    content = re.sub(
        r'(public\s+void\s+sendTyping\s*\([^)]*\)\s*\{)',
        r'\1 return; // Graniton Ghost Mode: Never leak typing/recording status',
        content,
        count=1
    )
    print("MessagesController: Enabled Ghost Mode (sendTyping disabled)")

    # 2. Anti-Delete: Ignore remote message deletion updates
    content = content.replace(
        "if (update instanceof TLRPC.TL_updateDeleteMessages)",
        "if (false && update instanceof TLRPC.TL_updateDeleteMessages)"
    )
    content = content.replace(
        "if (update instanceof TLRPC.TL_updateDeleteChannelMessages)",
        "if (false && update instanceof TLRPC.TL_updateDeleteChannelMessages)"
    )
    content = content.replace(
        "else if (update instanceof TLRPC.TL_updateDeleteMessages)",
        "else if (false && update instanceof TLRPC.TL_updateDeleteMessages)"
    )
    content = content.replace(
        "else if (update instanceof TLRPC.TL_updateDeleteChannelMessages)",
        "else if (false && update instanceof TLRPC.TL_updateDeleteChannelMessages)"
    )
    print("MessagesController: Enabled Anti-Delete protection")

    # 3. Bypass isPeerNoForwards and isChatNoForwards
    content = re.sub(
        r'(public\s+boolean\s+isPeerNoForwards\s*\([^)]*\)\s*\{)',
        r'\1 return false; // Graniton Bypass',
        content
    )
    content = re.sub(
        r'(public\s+boolean\s+isChatNoForwards\s*\([^)]*\)\s*\{)',
        r'\1 return false; // Graniton Bypass',
        content
    )
    print("MessagesController: Bypassed isPeerNoForwards / isChatNoForwards")

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Successfully patched MessagesController.java")

def patch_message_restrictions():
    path = "./TMessagesProj/src/main/java/org/telegram/messenger/MessageObject.java"
    if not os.path.exists(path):
        print(f"File {path} not found")
        return

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Remove noforwards check in canForwardMessage
    if "&& !messageOwner.noforwards;" in content:
        content = content.replace("&& !messageOwner.noforwards;", "; // Graniton: Bypassed noforwards restriction", 1)
        print("MessageObject: Unlocked forwarding for restricted messages")

    # 2. Unlock copying code blocks
    if "hasCodeCopyButton = codeLength >= 75 && !noforwards;" in content:
        content = content.replace("hasCodeCopyButton = codeLength >= 75 && !noforwards;", "hasCodeCopyButton = codeLength >= 75;", 1)
        print("MessageObject: Unlocked code copy button")

    # 3. Remove all sponsored ads (isSponsored = false)
    if "public boolean isSponsored() {" in content:
        content = content.replace(
            "public boolean isSponsored() {",
            "public boolean isSponsored() { return false; } public boolean _unused_isSponsored() {",
            1
        )
        print("MessageObject: Disabled sponsored messages (Ad-Free)")

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Successfully patched MessageObject.java")

def patch_user_config_premium():
    path = "./TMessagesProj/src/main/java/org/telegram/messenger/UserConfig.java"
    if not os.path.exists(path):
        print(f"File {path} not found")
        return

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    old_is_premium = '''    public boolean isPremium() {
        TLRPC.User user = currentUser;
        if (user == null) {
            return false;
        }
        return user.premium;
    }'''
    new_is_premium = '''    public boolean isPremium() {
        return true; // Graniton: Client-side Premium Features Unlocked
    }
    public boolean _real_isPremium() {
        TLRPC.User user = currentUser;
        if (user == null) {
            return false;
        }
        return user.premium;
    }'''

    if old_is_premium in content:
        content = content.replace(old_is_premium, new_is_premium, 1)
        print("UserConfig: Unlocked client-side Premium features")

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Successfully patched UserConfig.java")

def patch_force_120hz():
    path = "./TMessagesProj/src/main/java/org/telegram/ui/LaunchActivity.java"
    if not os.path.exists(path):
        print(f"File {path} not found")
        return

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    old_target = "        flagSecureReason.attach();\n\n        super.onCreate(savedInstanceState);"
    new_target = """        flagSecureReason.attach();

        super.onCreate(savedInstanceState);

        // Graniton: Force 120Hz display refresh rate on Galaxy S26 Ultra
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.M) {
            try {
                android.view.Display display = getWindowManager().getDefaultDisplay();
                android.view.Display.Mode[] modes = display.getSupportedModes();
                android.view.Display.Mode maxMode = null;
                float maxRate = 0;
                for (android.view.Display.Mode m : modes) {
                    if (m.getRefreshRate() > maxRate) {
                        maxRate = m.getRefreshRate();
                        maxMode = m;
                    }
                }
                if (maxMode != null && maxRate >= 90f) {
                    android.view.WindowManager.LayoutParams lp = getWindow().getAttributes();
                    lp.preferredDisplayModeId = maxMode.getModeId();
                    getWindow().setAttributes(lp);
                }
            } catch (Throwable ignore) {}
        }"""

    if old_target in content:
        content = content.replace(old_target, new_target, 1)
        print("LaunchActivity: Injected 120Hz force lock")

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Successfully patched LaunchActivity.java")

if __name__ == "__main__":
    patch_instant_camera_hd()
    patch_ghost_and_anti_delete()
    patch_message_restrictions()
    patch_user_config_premium()
    patch_force_120hz()
