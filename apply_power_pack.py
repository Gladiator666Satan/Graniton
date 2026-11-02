#!/usr/bin/env python3
"""
Graniton Power-Pack Mod Script
- HD 60fps Round Video Notes (Preserve 384x384 circular video message format, 60fps framerate, 2.5Mbps studio bitrate)
- True Ghost Mode (Disable sending typing, audio/video recording status)
- Anti-Delete Protection (Ignore incoming remote message deletions)
- Bypass Restricted Content (Save media, draw share button, and copy from noforwards channels)
- Ad-Free (Block sponsored channel messages)
- Media Spoiler Fix (Ensure outgoing photo and video spoilers are properly transmitted to recipient via MTProto)
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

    # 3. Boost bitrate to 2.5Mbps (Keep diameter at 384 so server accepts round_message: true)
    old_res = '''            int resolution = MessagesController.getInstance(currentAccount).roundVideoSize;
            int bitrate = MessagesController.getInstance(currentAccount).roundVideoBitrate * 1024;'''
    new_res = '''            int resolution = MessagesController.getInstance(currentAccount).roundVideoSize; // 384 server-compliant circular diameter
            int bitrate = 2500000; // 2.5 Mbps High Studio Bitrate'''
    if old_res in content:
        content = content.replace(old_res, new_res, 1)
        print("InstantCameraView: Boosted bitrate to 2.5Mbps")

    # 4. Boost videoEditedInfo bitrate
    content = content.replace("videoEditedInfo.bitrate = 1000000;", "videoEditedInfo.bitrate = 2500000;")

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

    # 1. Round video size (384 native diameter) & bitrate default (2500)
    old_defaults = '''        roundVideoSize = mainPreferences.getInt("roundVideoSize", 384);
        roundVideoBitrate = mainPreferences.getInt("roundVideoBitrate", 1000);'''
    new_defaults = '''        roundVideoSize = mainPreferences.getInt("roundVideoSize", 384);
        roundVideoBitrate = mainPreferences.getInt("roundVideoBitrate", 2500);'''
    if old_defaults in content:
        content = content.replace(old_defaults, new_defaults, 1)
        print("MessagesController: Set default roundVideoSize=384, roundVideoBitrate=2500")

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

def patch_media_spoilers():
    # 1. SendMessagesHelper.java
    smh_path = "./TMessagesProj/src/main/java/org/telegram/messenger/SendMessagesHelper.java"
    if os.path.exists(smh_path):
        with open(smh_path, "r", encoding="utf-8") as f:
            smh = f.read()

        smh_target = """    @UiThread
    public static void prepareSendingPhoto(AccountInstance accountInstance, String imageFilePath, String thumbFilePath, Uri imageUri, long dialogId, MessageObject replyToMsg, MessageObject replyToTopMsg, TL_stories.StoryItem storyItem, ChatActivity.ReplyQuote quote, ArrayList<TLRPC.MessageEntity> entities, ArrayList<TLRPC.InputDocument> stickers, InputContentInfoCompat inputContent, int ttl, MessageObject editingMessageObject, VideoEditedInfo videoEditedInfo, boolean notify, int scheduleDate, int scheduleRepeatPeriod, int mode, boolean forceDocument, CharSequence caption, SendMessageChatArguments sendMessageChatArguments, long effectId, long payStars, long monoForumPeerId, MessageSuggestionParams suggestionParams) {
        SendingMediaInfo info = new SendingMediaInfo();
        info.path = imageFilePath;
        info.thumbPath = thumbFilePath;
        info.uri = imageUri;
        if (caption != null) {
            info.caption = caption.toString();
        }
        info.entities = entities;
        info.ttl = ttl;
        if (stickers != null) {
            info.masks = new ArrayList<>(stickers);
        }
        info.videoEditedInfo = videoEditedInfo;
        ArrayList<SendingMediaInfo> infos = new ArrayList<>();
        infos.add(info);
        prepareSendingMedia(accountInstance, infos, dialogId, replyToMsg, replyToTopMsg, null, quote, forceDocument, false, editingMessageObject, notify, scheduleDate, 0, mode, false, inputContent, sendMessageChatArguments, effectId, false, payStars, monoForumPeerId, suggestionParams);
    }"""

        smh_replacement = """    @UiThread
    public static void prepareSendingPhoto(AccountInstance accountInstance, String imageFilePath, String thumbFilePath, Uri imageUri, long dialogId, MessageObject replyToMsg, MessageObject replyToTopMsg, TL_stories.StoryItem storyItem, ChatActivity.ReplyQuote quote, ArrayList<TLRPC.MessageEntity> entities, ArrayList<TLRPC.InputDocument> stickers, InputContentInfoCompat inputContent, int ttl, MessageObject editingMessageObject, VideoEditedInfo videoEditedInfo, boolean notify, int scheduleDate, int scheduleRepeatPeriod, int mode, boolean forceDocument, CharSequence caption, SendMessageChatArguments sendMessageChatArguments, long effectId, long payStars, long monoForumPeerId, MessageSuggestionParams suggestionParams) {
        prepareSendingPhoto(accountInstance, imageFilePath, thumbFilePath, imageUri, dialogId, replyToMsg, replyToTopMsg, storyItem, quote, entities, stickers, inputContent, ttl, editingMessageObject, videoEditedInfo, notify, scheduleDate, scheduleRepeatPeriod, mode, forceDocument, caption, sendMessageChatArguments, effectId, payStars, monoForumPeerId, suggestionParams, false);
    }

    @UiThread
    public static void prepareSendingPhoto(AccountInstance accountInstance, String imageFilePath, String thumbFilePath, Uri imageUri, long dialogId, MessageObject replyToMsg, MessageObject replyToTopMsg, TL_stories.StoryItem storyItem, ChatActivity.ReplyQuote quote, ArrayList<TLRPC.MessageEntity> entities, ArrayList<TLRPC.InputDocument> stickers, InputContentInfoCompat inputContent, int ttl, MessageObject editingMessageObject, VideoEditedInfo videoEditedInfo, boolean notify, int scheduleDate, int scheduleRepeatPeriod, int mode, boolean forceDocument, CharSequence caption, SendMessageChatArguments sendMessageChatArguments, long effectId, long payStars, long monoForumPeerId, MessageSuggestionParams suggestionParams, boolean hasMediaSpoilers) {
        SendingMediaInfo info = new SendingMediaInfo();
        info.path = imageFilePath;
        info.thumbPath = thumbFilePath;
        info.uri = imageUri;
        if (caption != null) {
            info.caption = caption.toString();
        }
        info.entities = entities;
        info.ttl = ttl;
        if (stickers != null) {
            info.masks = new ArrayList<>(stickers);
        }
        info.videoEditedInfo = videoEditedInfo;
        info.hasMediaSpoilers = hasMediaSpoilers;
        ArrayList<SendingMediaInfo> infos = new ArrayList<>();
        infos.add(info);
        prepareSendingMedia(accountInstance, infos, dialogId, replyToMsg, replyToTopMsg, null, quote, forceDocument, false, editingMessageObject, notify, scheduleDate, 0, mode, false, inputContent, sendMessageChatArguments, effectId, false, payStars, monoForumPeerId, suggestionParams);
    }"""

        if smh_target in smh:
            smh = smh.replace(smh_target, smh_replacement, 1)
            with open(smh_path, "w", encoding="utf-8") as f:
                f.write(smh)
            print("SendMessagesHelper: Added hasMediaSpoilers to prepareSendingPhoto")
        else:
            print("WARNING: smh_target not found in SendMessagesHelper.java")

    # 2. ChatActivity.java
    chat_path = "./TMessagesProj/src/main/java/org/telegram/ui/ChatActivity.java"
    if os.path.exists(chat_path):
        with open(chat_path, "r", encoding="utf-8") as f:
            chat = f.read()

        target_group = """                info.canDeleteAfter = entry.canDeleteAfter;
                info.highQuality = entry.isHighQuality();
                photos.add(info);"""
        rep_group = """                info.canDeleteAfter = entry.canDeleteAfter;
                info.highQuality = entry.isHighQuality();
                info.hasMediaSpoilers = entry.hasSpoiler;
                photos.add(info);"""
        if target_group in chat:
            chat = chat.replace(target_group, rep_group, 1)
            print("ChatActivity: Enabled spoiler flag in sendPhotosGroup")

        target_edit = """                    if (photoEntry.imagePath != null) {
                        SendMessagesHelper.prepareSendingPhoto(getAccountInstance(), photoEntry.imagePath, photoEntry.thumbPath, null, dialog_id, editingMessageObject, getThreadMessage(), null, replyingQuote, photoEntry.entities, photoEntry.stickers, null, photoEntry.ttl, null, videoEditedInfo, notify, scheduleDate, scheduleRepeatPeriod, 0, forceDocument, photoEntry.caption, getMessageChatSendParams(), photoEntry.effectId, payStars, getSendMonoForumPeerId(), params);
                    } else if (photoEntry.path != null) {
                        SendMessagesHelper.prepareSendingPhoto(getAccountInstance(), photoEntry.path, photoEntry.thumbPath, null, dialog_id, editingMessageObject, getThreadMessage(), null, replyingQuote, photoEntry.entities, photoEntry.stickers, null, photoEntry.ttl, null, videoEditedInfo, notify, scheduleDate, scheduleRepeatPeriod, 0, forceDocument, photoEntry.caption, getMessageChatSendParams(), photoEntry.effectId, payStars, getSendMonoForumPeerId(), params);
                    }"""
        rep_edit = """                    if (photoEntry.imagePath != null) {
                        SendMessagesHelper.prepareSendingPhoto(getAccountInstance(), photoEntry.imagePath, photoEntry.thumbPath, null, dialog_id, editingMessageObject, getThreadMessage(), null, replyingQuote, photoEntry.entities, photoEntry.stickers, null, photoEntry.ttl, null, videoEditedInfo, notify, scheduleDate, scheduleRepeatPeriod, 0, forceDocument, photoEntry.caption, getMessageChatSendParams(), photoEntry.effectId, payStars, getSendMonoForumPeerId(), params, photoEntry.hasSpoiler);
                    } else if (photoEntry.path != null) {
                        SendMessagesHelper.prepareSendingPhoto(getAccountInstance(), photoEntry.path, photoEntry.thumbPath, null, dialog_id, editingMessageObject, getThreadMessage(), null, replyingQuote, photoEntry.entities, photoEntry.stickers, null, photoEntry.ttl, null, videoEditedInfo, notify, scheduleDate, scheduleRepeatPeriod, 0, forceDocument, photoEntry.caption, getMessageChatSendParams(), photoEntry.effectId, payStars, getSendMonoForumPeerId(), params, photoEntry.hasSpoiler);
                    }"""
        if target_edit in chat:
            chat = chat.replace(target_edit, rep_edit, 1)
            print("ChatActivity: Enabled spoiler in sendMedia (editing)")

        target_norm = """                    if (photoEntry.imagePath != null) {
                        SendMessagesHelper.prepareSendingPhoto(getAccountInstance(), photoEntry.imagePath, photoEntry.thumbPath, null, dialog_id, replyingMessageObject, getThreadMessage(), null, replyingQuote, photoEntry.entities, photoEntry.stickers, null, photoEntry.ttl, editingMessageObject, videoEditedInfo, notify, scheduleDate, scheduleRepeatPeriod, 0, forceDocument, photoEntry.caption, getMessageChatSendParams(), photoEntry.effectId, payStars, getSendMonoForumPeerId(), getSendMessageSuggestionParams());
                    } else if (photoEntry.path != null) {
                        SendMessagesHelper.prepareSendingPhoto(getAccountInstance(), photoEntry.path, photoEntry.thumbPath, null, dialog_id, replyingMessageObject, getThreadMessage(), null, replyingQuote, photoEntry.entities, photoEntry.stickers, null, photoEntry.ttl, editingMessageObject, videoEditedInfo, notify, scheduleDate, scheduleRepeatPeriod, 0, forceDocument, photoEntry.caption, getMessageChatSendParams(), photoEntry.effectId, payStars, getSendMonoForumPeerId(), getSendMessageSuggestionParams());
                    }"""
        rep_norm = """                    if (photoEntry.imagePath != null) {
                        SendMessagesHelper.prepareSendingPhoto(getAccountInstance(), photoEntry.imagePath, photoEntry.thumbPath, null, dialog_id, replyingMessageObject, getThreadMessage(), null, replyingQuote, photoEntry.entities, photoEntry.stickers, null, photoEntry.ttl, editingMessageObject, videoEditedInfo, notify, scheduleDate, scheduleRepeatPeriod, 0, forceDocument, photoEntry.caption, getMessageChatSendParams(), photoEntry.effectId, payStars, getSendMonoForumPeerId(), getSendMessageSuggestionParams(), photoEntry.hasSpoiler);
                    } else if (photoEntry.path != null) {
                        SendMessagesHelper.prepareSendingPhoto(getAccountInstance(), photoEntry.path, photoEntry.thumbPath, null, dialog_id, replyingMessageObject, getThreadMessage(), null, replyingQuote, photoEntry.entities, photoEntry.stickers, null, photoEntry.ttl, editingMessageObject, videoEditedInfo, notify, scheduleDate, scheduleRepeatPeriod, 0, forceDocument, photoEntry.caption, getMessageChatSendParams(), photoEntry.effectId, payStars, getSendMonoForumPeerId(), getSendMessageSuggestionParams(), photoEntry.hasSpoiler);
                    }"""
        if target_norm in chat:
            chat = chat.replace(target_norm, rep_norm, 1)
            print("ChatActivity: Enabled spoiler in sendMedia (normal)")

        with open(chat_path, "w", encoding="utf-8") as f:
            f.write(chat)

    # 3. PhotoViewer.java
    pv_path = "./TMessagesProj/src/main/java/org/telegram/ui/PhotoViewer.java"
    if os.path.exists(pv_path):
        with open(pv_path, "r", encoding="utf-8") as f:
            pv = f.read()

        target_pv = """                                if (photoEntry.imagePath != null) {
                                    SendMessagesHelper.prepareSendingPhoto(parentChatActivity.getAccountInstance(), photoEntry.imagePath, photoEntry.thumbPath, null, parentChatActivity.getDialogId(), replyToMsg, parentChatActivity.getThreadMessage(), null, replyQuote, photoEntry.entities, photoEntry.stickers, null, photoEntry.ttl, editingMessageObject, videoEditedInfo, notify, scheduleDate, scheduleRepeatPeriod, 0, forceDocument, photoEntry.caption, parentChatActivity.getMessageChatSendParams(), 0, 0, parentChatActivity.getSendMonoForumPeerId(), parentChatActivity.getSendMessageSuggestionParams());
                                } else if (photoEntry.path != null) {
                                    SendMessagesHelper.prepareSendingPhoto(parentChatActivity.getAccountInstance(), photoEntry.path, photoEntry.thumbPath, null, parentChatActivity.getDialogId(), replyToMsg, parentChatActivity.getThreadMessage(), null, replyQuote, photoEntry.entities, photoEntry.stickers, null, photoEntry.ttl, editingMessageObject, videoEditedInfo, notify, scheduleDate, scheduleRepeatPeriod, 0, forceDocument, photoEntry.caption, parentChatActivity.getMessageChatSendParams(), 0, 0, parentChatActivity.getSendMonoForumPeerId(), parentChatActivity.getSendMessageSuggestionParams());
                                }"""
        rep_pv = """                                if (photoEntry.imagePath != null) {
                                    SendMessagesHelper.prepareSendingPhoto(parentChatActivity.getAccountInstance(), photoEntry.imagePath, photoEntry.thumbPath, null, parentChatActivity.getDialogId(), replyToMsg, parentChatActivity.getThreadMessage(), null, replyQuote, photoEntry.entities, photoEntry.stickers, null, photoEntry.ttl, editingMessageObject, videoEditedInfo, notify, scheduleDate, scheduleRepeatPeriod, 0, forceDocument, photoEntry.caption, parentChatActivity.getMessageChatSendParams(), 0, 0, parentChatActivity.getSendMonoForumPeerId(), parentChatActivity.getSendMessageSuggestionParams(), photoEntry.hasSpoiler);
                                } else if (photoEntry.path != null) {
                                    SendMessagesHelper.prepareSendingPhoto(parentChatActivity.getAccountInstance(), photoEntry.path, photoEntry.thumbPath, null, parentChatActivity.getDialogId(), replyToMsg, parentChatActivity.getThreadMessage(), null, replyQuote, photoEntry.entities, photoEntry.stickers, null, photoEntry.ttl, editingMessageObject, videoEditedInfo, notify, scheduleDate, scheduleRepeatPeriod, 0, forceDocument, photoEntry.caption, parentChatActivity.getMessageChatSendParams(), 0, 0, parentChatActivity.getSendMonoForumPeerId(), parentChatActivity.getSendMessageSuggestionParams(), photoEntry.hasSpoiler);
                                }"""
        if target_pv in pv:
            pv = pv.replace(target_pv, rep_pv, 1)
            with open(pv_path, "w", encoding="utf-8") as f:
                f.write(pv)
            print("PhotoViewer: Enabled spoiler in sendButtonPressed")
        else:
            print("WARNING: target_pv not found in PhotoViewer.java")

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
    patch_media_spoilers()
    patch_force_120hz()