#!/usr/bin/env python3
"""
Graniton Power-Pack Mod Script
- HD 60fps Round Video Notes (720p @ 60fps + 4.5Mbps bitrate)
- True Ghost Mode (Disable sending typing, audio/video recording status)
- Anti-Delete Protection (Ignore incoming remote message deletions)
- Bypass Restricted Content (Save media, draw share button, and copy from noforwards channels)
- Ad-Free (Block sponsored channel messages)
- Force 120Hz Smooth Motion on Galaxy S26 Ultra
"""
import os

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

    # 2. Boost edited info frame rate
    if "videoEditedInfo.framerate = 25;" in content:
        content = content.replace("videoEditedInfo.framerate = 25;", "videoEditedInfo.framerate = 60;")
        print("InstantCameraView: Set videoEditedInfo.framerate = 60")

    # 3. Boost resolution to 720p and bitrate to 4.5Mbps
    old_res = '''            int resolution = MessagesController.getInstance(currentAccount).roundVideoSize;
            int bitrate = MessagesController.getInstance(currentAccount).roundVideoBitrate * 1024;'''
    new_res = '''            int resolution = 720; // Graniton HD Round Video (720x720)
            int bitrate = 4500000; // 4.5 Mbps Studio Bitrate'''
    if old_res in content:
        content = content.replace(old_res, new_res, 1)
        print("InstantCameraView: Boosted resolution to 720p & bitrate to 4.5Mbps")

    # 4. Boost videoEditedInfo result dimensions and bitrate
    content = content.replace("videoEditedInfo.resultWidth = videoEditedInfo.originalWidth = 360;", "videoEditedInfo.resultWidth = videoEditedInfo.originalWidth = 720;")
    content = content.replace("videoEditedInfo.resultHeight = videoEditedInfo.originalHeight = 360;", "videoEditedInfo.resultHeight = videoEditedInfo.originalHeight = 720;")
    content = content.replace("videoEditedInfo.bitrate = 1000000;", "videoEditedInfo.bitrate = 4500000;")
    print("InstantCameraView: Updated videoEditedInfo dimensions to 720x720 and 4.5Mbps")

    # 5. Always allow big size camera
    content = content.replace(
        "private boolean allowBigSizeCamera() {",
        "private boolean allowBigSizeCamera() { return true; } private boolean _unused_allowBigSizeCamera() {",
        1
    )
    print("InstantCameraView: Always allow big size camera")

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

    # 1. Round video size & bitrate default
    old_defaults = '''        roundVideoSize = mainPreferences.getInt("roundVideoSize", 384);
        roundVideoBitrate = mainPreferences.getInt("roundVideoBitrate", 1000);'''
    new_defaults = '''        roundVideoSize = mainPreferences.getInt("roundVideoSize", 720);
        roundVideoBitrate = mainPreferences.getInt("roundVideoBitrate", 4500);'''
    if old_defaults in content:
        content = content.replace(old_defaults, new_defaults, 1)
        print("MessagesController: Set default roundVideoSize=720, roundVideoBitrate=4500")

    # 2. True Ghost Mode: Disable sending typing status (valid Java method stubs)
    old_typing1 = "public boolean sendTyping(long dialogId, long threadMsgId, int action, int classGuid) {"
    new_typing1 = "public boolean sendTyping(long dialogId, long threadMsgId, int action, int classGuid) { return false; } public boolean _unused_sendTyping1(long dialogId, long threadMsgId, int action, int classGuid) {"
    if old_typing1 in content:
        content = content.replace(old_typing1, new_typing1, 1)

    old_typing2 = "public boolean sendTyping(long dialogId, long threadMsgId, int action, String emojicon, int classGuid) {"
    new_typing2 = "public boolean sendTyping(long dialogId, long threadMsgId, int action, String emojicon, int classGuid) { return false; } public boolean _unused_sendTyping2(long dialogId, long threadMsgId, int action, String emojicon, int classGuid) {"
    if old_typing2 in content:
        content = content.replace(old_typing2, new_typing2, 1)
    print("MessagesController: Enabled Ghost Mode (sendTyping returns false)")

    # 3. Anti-Delete: Ignore incoming message deletion updates
    t1 = '''deletedMessages.put(0, arrayList);
                }
                arrayList.addAll(update.messages);'''
    t1_rep = '''deletedMessages.put(0, arrayList);
                }
                // arrayList.addAll(update.messages); // Graniton Anti-Delete'''
    if t1 in content:
        content = content.replace(t1, t1_rep, 1)

    t2 = '''deletedMessages.put(dialogId, arrayList);
                }
                arrayList.addAll(update.messages);'''
    t2_rep = '''deletedMessages.put(dialogId, arrayList);
                }
                // arrayList.addAll(update.messages); // Graniton Anti-Delete'''
    if t2 in content:
        content = content.replace(t2, t2_rep, 1)
    print("MessagesController: Enabled Anti-Delete protection")

    # 4. Bypass noforwards checks in MessagesController
    chat_forwards = "public boolean isChatNoForwards(TLRPC.Chat chat) {"
    chat_forwards_rep = "public boolean isChatNoForwards(TLRPC.Chat chat) { return false; } public boolean _unused_isChatNoForwardsChat(TLRPC.Chat chat) {"
    if chat_forwards in content:
        content = content.replace(chat_forwards, chat_forwards_rep, 1)

    chat_forwards_id = "public boolean isChatNoForwards(long chatId) {"
    chat_forwards_id_rep = "public boolean isChatNoForwards(long chatId) { return false; } public boolean _unused_isChatNoForwardsId(long chatId) {"
    if chat_forwards_id in content:
        content = content.replace(chat_forwards_id, chat_forwards_id_rep, 1)

    peer_forwards = "public boolean isPeerNoForwards(long dialogId) {"
    peer_forwards_rep = "public boolean isPeerNoForwards(long dialogId) { return false; } public boolean _unused_isPeerNoForwards(long dialogId) {"
    if peer_forwards in content:
        content = content.replace(peer_forwards, peer_forwards_rep, 1)

    user_forwards = "public boolean isUserNoForwards(TLRPC.UserFull userFull) {"
    user_forwards_rep = "public boolean isUserNoForwards(TLRPC.UserFull userFull) { return false; } public boolean _unused_isUserNoForwards(TLRPC.UserFull userFull) {"
    if user_forwards in content:
        content = content.replace(user_forwards, user_forwards_rep, 1)
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

    # 3. Unlock share button in restricted channels
    old_share = '''        } else if (messageOwner.noforwards) {
            return false;'''
    new_share = '''        } else if (messageOwner.noforwards) {
            // Graniton: bypass noforwards to allow share button'''
    if old_share in content:
        content = content.replace(old_share, new_share, 1)
        print("MessageObject: Unlocked share button for restricted messages")

    # 4. Remove all sponsored ads (isSponsored = false)
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
    patch_force_120hz()
