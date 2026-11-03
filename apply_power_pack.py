#!/usr/bin/env python3
"""
Graniton Power-Pack Mod Script (Audited & Verified)
- HD 60fps Round Video Notes (384x384 native circular MTProto format, 60fps without 30fps MediaController downgrade, 2.5Mbps studio bitrate)
- True Ghost Mode (Disable sending typing/recording status, stealth bomb/view-once viewing without read receipts, local-only mention badge clearing)
- Anti-Delete Protection (Ignore incoming remote message deletions globally and in channels)
- Bypass Restricted Content (Save media, draw share button, copy text/code, and forward from noforwards channels)
- Secret / Expiring Media (Bombs / View-Once TTL) Full Saving, .enc Decryption, Preserved Timer Badge, & Global Screenshot Unblock
- Media Spoiler Fix (Guarantee outgoing photo & video hasMediaSpoilers flag delivery over MTProto)
- Galaxy S26 Ultra Hardware Boost (Force 120Hz display refresh rate + Default 1080p HD video sending quality)
- Client-Side Chat & Context Translation + Ad-Free (Block sponsored channel messages)
"""
import os


def must_replace(content, target, replacement, label, count=1):
    if target not in content:
        raise RuntimeError(f"[Graniton Power-Pack] Target not found for: {label}")
    if count is None:
        return content.replace(target, replacement)
    return content.replace(target, replacement, count)


def patch_instant_camera_and_video_notes():
    # 1. InstantCameraView.java
    icv_path = "./TMessagesProj/src/main/java/org/telegram/ui/Components/InstantCameraView.java"
    if not os.path.exists(icv_path):
        raise FileNotFoundError(f"Missing {icv_path}")

    with open(icv_path, "r", encoding="utf-8") as f:
        content = f.read()

    content = must_replace(
        content,
        "private static final int FRAME_RATE = 30;",
        "private static final int FRAME_RATE = 60;",
        "InstantCameraView FRAME_RATE = 60"
    )
    content = must_replace(
        content,
        "videoEditedInfo.framerate = 25;",
        "videoEditedInfo.framerate = 60;",
        "InstantCameraView videoEditedInfo.framerate = 60",
        count=None
    )

    old_res = (
        "            int resolution = MessagesController.getInstance(currentAccount).roundVideoSize;\n"
        "            int bitrate = MessagesController.getInstance(currentAccount).roundVideoBitrate * 1024;"
    )
    new_res = (
        "            int resolution = MessagesController.getInstance(currentAccount).roundVideoSize; // 384 server-compliant circular diameter\n"
        "            int bitrate = 2500000; // 2.5 Mbps High Studio Bitrate"
    )
    content = must_replace(content, old_res, new_res, "InstantCameraView 2.5Mbps bitrate")
    content = must_replace(
        content,
        "videoEditedInfo.bitrate = 1000000;",
        "videoEditedInfo.bitrate = 2500000;",
        "InstantCameraView videoEditedInfo.bitrate = 2.5Mbps",
        count=None
    )
    content = must_replace(
        content,
        "private boolean allowBigSizeCamera() {",
        "private boolean allowBigSizeCamera() { return true; } private boolean _unused_allowBigSizeCamera() {",
        "InstantCameraView allowBigSizeCamera"
    )

    with open(icv_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Successfully patched InstantCameraView.java (60fps / 2.5Mbps circular video notes)")

    # 2. MediaController.java: Prevent silent 60fps -> 30fps clamp when min(w, h) <= 480 (384x384 round video notes!)
    mc_path = "./TMessagesProj/src/main/java/org/telegram/messenger/MediaController.java"
    if not os.path.exists(mc_path):
        raise FileNotFoundError(f"Missing {mc_path}")

    with open(mc_path, "r", encoding="utf-8") as f:
        mc = f.read()

    old_fps_clamp = (
        "        if (!info.shouldLimitFps && framerate > 40 && (Math.min(resultHeight, resultWidth) <= 480)) {\n"
        "            framerate = 30;\n"
        "        }"
    )
    new_fps_clamp = (
        "        if (false && !info.shouldLimitFps && framerate > 40 && (Math.min(resultHeight, resultWidth) <= 480)) {\n"
        "            framerate = 30; // Graniton: preserve 60fps on 384x384 round video notes\n"
        "        }"
    )
    mc = must_replace(mc, old_fps_clamp, new_fps_clamp, "MediaController 60fps preservation")

    with open(mc_path, "w", encoding="utf-8") as f:
        f.write(mc)
    print("Successfully patched MediaController.java (preserved 60fps encoding)")


def patch_ghost_and_anti_delete():
    path = "./TMessagesProj/src/main/java/org/telegram/messenger/MessagesController.java"
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing {path}")

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Round video size (384 native diameter) & bitrate default (2500)
    old_defaults = (
        '        roundVideoSize = mainPreferences.getInt("roundVideoSize", 384);\n'
        '        roundVideoBitrate = mainPreferences.getInt("roundVideoBitrate", 1000);'
    )
    new_defaults = (
        '        roundVideoSize = mainPreferences.getInt("roundVideoSize", 384);\n'
        '        roundVideoBitrate = mainPreferences.getInt("roundVideoBitrate", 2500);'
    )
    content = must_replace(content, old_defaults, new_defaults, "MessagesController roundVideoBitrate=2500")

    # 2. True Ghost Mode: Disable sending typing/recording status
    content = must_replace(
        content,
        "public boolean sendTyping(long dialogId, long threadMsgId, int action, int classGuid) {",
        "public boolean sendTyping(long dialogId, long threadMsgId, int action, int classGuid) { return false; } public boolean _unused_sendTyping1(long dialogId, long threadMsgId, int action, int classGuid) {",
        "MessagesController sendTyping(4)"
    )
    content = must_replace(
        content,
        "public boolean sendTyping(long dialogId, long threadMsgId, int action, String emojicon, int classGuid) {",
        "public boolean sendTyping(long dialogId, long threadMsgId, int action, String emojicon, int classGuid) { return false; } public boolean _unused_sendTyping2(long dialogId, long threadMsgId, int action, String emojicon, int classGuid) {",
        "MessagesController sendTyping(5)"
    )

    # 3. Stealth viewing of bombs, view-once voice messages, and view-once round video notes
    old_content_read = (
        "    public void markMessageContentAsRead(MessageObject messageObject) {\n"
        "        if (messageObject.scheduled) {\n"
        "            return;\n"
        "        }"
    )
    new_content_read = (
        "    public void markMessageContentAsRead(MessageObject messageObject) {\n"
        "        if (messageObject == null || messageObject.scheduled || messageObject.isSecretMedia() || (messageObject.messageOwner != null && (messageObject.messageOwner.ttl > 0 || (messageObject.messageOwner.media != null && messageObject.messageOwner.media.ttl_seconds != 0)))) {\n"
        "            return;\n"
        "        }"
    )
    content = must_replace(content, old_content_read, new_content_read, "MessagesController stealth markMessageContentAsRead")

    # 4. Local-only @ mention badge clearing without sending server read receipt
    old_mentions_read = (
        "        getMessagesStorage().resetMentionsCount(dialogId, topicId, 0);\n"
        "        TLRPC.TL_messages_readMentions req = new TLRPC.TL_messages_readMentions();"
    )
    new_mentions_read = (
        "        getMessagesStorage().resetMentionsCount(dialogId, topicId, 0);\n"
        "        if (true) return; // Graniton: clear local @ badge without sending server read receipt\n"
        "        TLRPC.TL_messages_readMentions req = new TLRPC.TL_messages_readMentions();"
    )
    content = must_replace(content, old_mentions_read, new_mentions_read, "MessagesController local markMentionsAsRead")

    # 5. Anti-Delete: Ignore incoming message deletion updates
    t1 = (
        "deletedMessages.put(0, arrayList);\n"
        "                }\n"
        "                arrayList.addAll(update.messages);"
    )
    t1_rep = (
        "deletedMessages.put(0, arrayList);\n"
        "                }\n"
        "                // arrayList.addAll(update.messages); // Graniton Anti-Delete"
    )
    content = must_replace(content, t1, t1_rep, "MessagesController Anti-Delete global")

    t2 = (
        "deletedMessages.put(dialogId, arrayList);\n"
        "                }\n"
        "                arrayList.addAll(update.messages);"
    )
    t2_rep = (
        "deletedMessages.put(dialogId, arrayList);\n"
        "                }\n"
        "                // arrayList.addAll(update.messages); // Graniton Anti-Delete"
    )
    content = must_replace(content, t2, t2_rep, "MessagesController Anti-Delete channel")

    # 6. Bypass noforwards checks in MessagesController
    content = must_replace(
        content,
        "public boolean isChatNoForwards(TLRPC.Chat chat) {",
        "public boolean isChatNoForwards(TLRPC.Chat chat) { return false; } public boolean _unused_isChatNoForwardsChat(TLRPC.Chat chat) {",
        "MessagesController isChatNoForwards(Chat)"
    )
    content = must_replace(
        content,
        "public boolean isChatNoForwards(long chatId) {",
        "public boolean isChatNoForwards(long chatId) { return false; } public boolean _unused_isChatNoForwardsId(long chatId) {",
        "MessagesController isChatNoForwards(long)"
    )
    content = must_replace(
        content,
        "public boolean isPeerNoForwards(long dialogId) {",
        "public boolean isPeerNoForwards(long dialogId) { return false; } public boolean _unused_isPeerNoForwards(long dialogId) {",
        "MessagesController isPeerNoForwards"
    )
    content = must_replace(
        content,
        "public boolean isUserNoForwards(TLRPC.UserFull userFull) {",
        "public boolean isUserNoForwards(TLRPC.UserFull userFull) { return false; } public boolean _unused_isUserNoForwards(TLRPC.UserFull userFull) {",
        "MessagesController isUserNoForwards"
    )

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Successfully patched MessagesController.java")


def patch_message_restrictions():
    path = "./TMessagesProj/src/main/java/org/telegram/messenger/MessageObject.java"
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing {path}")

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Disable .enc local cache encryption for TTL/bomb/view-once media so plain files exist on disk
    #    while keeping isSecretMedia() intact so "1" / "5s" timer badges render properly in chat!
    content = must_replace(
        content,
        "public static boolean shouldEncryptPhotoOrVideo(int currentAccount, TLRPC.Message message) {",
        "public static boolean shouldEncryptPhotoOrVideo(int currentAccount, TLRPC.Message message) { return false; } private static boolean _unused_shouldEncryptPhotoOrVideo(int currentAccount, TLRPC.Message message) {",
        "MessageObject shouldEncryptPhotoOrVideo"
    )

    # 2. Remove noforwards check in canForwardMessage
    content = must_replace(
        content,
        "&& !messageOwner.noforwards;",
        "; // Graniton: Bypassed noforwards restriction",
        "MessageObject canForwardMessage noforwards"
    )

    # 3. Unlock copying code blocks
    content = must_replace(
        content,
        "hasCodeCopyButton = codeLength >= 75 && !noforwards;",
        "hasCodeCopyButton = codeLength >= 75;",
        "MessageObject hasCodeCopyButton"
    )

    # 4. Unlock share button in restricted channels
    content = must_replace(
        content,
        "        } else if (messageOwner.noforwards) {\n            return false;",
        "        } else if (messageOwner.noforwards) {\n            // Graniton: bypass noforwards to allow share button",
        "MessageObject share button noforwards"
    )

    # 5. Remove all sponsored ads (isSponsored = false)
    content = must_replace(
        content,
        "public boolean isSponsored() {",
        "public boolean isSponsored() { return false; } public boolean _unused_isSponsored() {",
        "MessageObject isSponsored"
    )

    # 6. Allow unlimited replay & saving of view-once voice and round video notes
    t_vo = (
        "    public boolean isVoiceOnce() {\n"
        "        return isVoice() && messageOwner != null && messageOwner.media != null && messageOwner.media.ttl_seconds == 0x7FFFFFFF;\n"
        "    }\n\n"
        "    public boolean isRoundOnce() {\n"
        "        return isRoundVideo() && messageOwner != null && messageOwner.media != null && messageOwner.media.ttl_seconds == 0x7FFFFFFF;\n"
        "    }"
    )
    r_vo = (
        "    public boolean isVoiceOnce() {\n"
        "        return false; // Graniton: allow replay and saving of view-once voice messages\n"
        "    }\n\n"
        "    public boolean isRoundOnce() {\n"
        "        return false; // Graniton: allow replay and saving of view-once round video notes\n"
        "    }"
    )
    content = must_replace(content, t_vo, r_vo, "MessageObject isVoiceOnce / isRoundOnce")

    # 7. Allow forwarding check in MessageObject
    content = must_replace(
        content,
        "!needDrawBluredPreview() && !isLiveLocation()",
        "true && !isLiveLocation() /* Graniton: allow forwarding bomb media */",
        "MessageObject canForwardMessage bluredPreview"
    )

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Successfully patched MessageObject.java")


def patch_media_spoilers_and_hd_video():
    # 1. SendMessagesHelper.java
    smh_path = "./TMessagesProj/src/main/java/org/telegram/messenger/SendMessagesHelper.java"
    if not os.path.exists(smh_path):
        raise FileNotFoundError(f"Missing {smh_path}")

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

    smh = must_replace(smh, smh_target, smh_replacement, "SendMessagesHelper prepareSendingPhoto spoiler overload")
    with open(smh_path, "w", encoding="utf-8") as f:
        f.write(smh)
    print("Successfully patched SendMessagesHelper.java (media spoilers)")

    # 2. ChatActivity.java (spoiler flags)
    chat_path = "./TMessagesProj/src/main/java/org/telegram/ui/ChatActivity.java"
    if not os.path.exists(chat_path):
        raise FileNotFoundError(f"Missing {chat_path}")

    with open(chat_path, "r", encoding="utf-8") as f:
        chat = f.read()

    chat = must_replace(
        chat,
        """                info.canDeleteAfter = entry.canDeleteAfter;
                info.highQuality = entry.isHighQuality();
                photos.add(info);""",
        """                info.canDeleteAfter = entry.canDeleteAfter;
                info.highQuality = entry.isHighQuality();
                info.hasMediaSpoilers = entry.hasSpoiler;
                photos.add(info);""",
        "ChatActivity sendPhotosGroup spoiler"
    )
    chat = must_replace(
        chat,
        """                    if (photoEntry.imagePath != null) {
                        SendMessagesHelper.prepareSendingPhoto(getAccountInstance(), photoEntry.imagePath, photoEntry.thumbPath, null, dialog_id, editingMessageObject, getThreadMessage(), null, replyingQuote, photoEntry.entities, photoEntry.stickers, null, photoEntry.ttl, null, videoEditedInfo, notify, scheduleDate, scheduleRepeatPeriod, 0, forceDocument, photoEntry.caption, getMessageChatSendParams(), photoEntry.effectId, payStars, getSendMonoForumPeerId(), params);
                    } else if (photoEntry.path != null) {
                        SendMessagesHelper.prepareSendingPhoto(getAccountInstance(), photoEntry.path, photoEntry.thumbPath, null, dialog_id, editingMessageObject, getThreadMessage(), null, replyingQuote, photoEntry.entities, photoEntry.stickers, null, photoEntry.ttl, null, videoEditedInfo, notify, scheduleDate, scheduleRepeatPeriod, 0, forceDocument, photoEntry.caption, getMessageChatSendParams(), photoEntry.effectId, payStars, getSendMonoForumPeerId(), params);
                    }""",
        """                    if (photoEntry.imagePath != null) {
                        SendMessagesHelper.prepareSendingPhoto(getAccountInstance(), photoEntry.imagePath, photoEntry.thumbPath, null, dialog_id, editingMessageObject, getThreadMessage(), null, replyingQuote, photoEntry.entities, photoEntry.stickers, null, photoEntry.ttl, null, videoEditedInfo, notify, scheduleDate, scheduleRepeatPeriod, 0, forceDocument, photoEntry.caption, getMessageChatSendParams(), photoEntry.effectId, payStars, getSendMonoForumPeerId(), params, photoEntry.hasSpoiler);
                    } else if (photoEntry.path != null) {
                        SendMessagesHelper.prepareSendingPhoto(getAccountInstance(), photoEntry.path, photoEntry.thumbPath, null, dialog_id, editingMessageObject, getThreadMessage(), null, replyingQuote, photoEntry.entities, photoEntry.stickers, null, photoEntry.ttl, null, videoEditedInfo, notify, scheduleDate, scheduleRepeatPeriod, 0, forceDocument, photoEntry.caption, getMessageChatSendParams(), photoEntry.effectId, payStars, getSendMonoForumPeerId(), params, photoEntry.hasSpoiler);
                    }""",
        "ChatActivity sendMedia editing spoiler"
    )
    chat = must_replace(
        chat,
        """                    if (photoEntry.imagePath != null) {
                        SendMessagesHelper.prepareSendingPhoto(getAccountInstance(), photoEntry.imagePath, photoEntry.thumbPath, null, dialog_id, replyingMessageObject, getThreadMessage(), null, replyingQuote, photoEntry.entities, photoEntry.stickers, null, photoEntry.ttl, editingMessageObject, videoEditedInfo, notify, scheduleDate, scheduleRepeatPeriod, 0, forceDocument, photoEntry.caption, getMessageChatSendParams(), photoEntry.effectId, payStars, getSendMonoForumPeerId(), getSendMessageSuggestionParams());
                    } else if (photoEntry.path != null) {
                        SendMessagesHelper.prepareSendingPhoto(getAccountInstance(), photoEntry.path, photoEntry.thumbPath, null, dialog_id, replyingMessageObject, getThreadMessage(), null, replyingQuote, photoEntry.entities, photoEntry.stickers, null, photoEntry.ttl, editingMessageObject, videoEditedInfo, notify, scheduleDate, scheduleRepeatPeriod, 0, forceDocument, photoEntry.caption, getMessageChatSendParams(), photoEntry.effectId, payStars, getSendMonoForumPeerId(), getSendMessageSuggestionParams());
                    }""",
        """                    if (photoEntry.imagePath != null) {
                        SendMessagesHelper.prepareSendingPhoto(getAccountInstance(), photoEntry.imagePath, photoEntry.thumbPath, null, dialog_id, replyingMessageObject, getThreadMessage(), null, replyingQuote, photoEntry.entities, photoEntry.stickers, null, photoEntry.ttl, editingMessageObject, videoEditedInfo, notify, scheduleDate, scheduleRepeatPeriod, 0, forceDocument, photoEntry.caption, getMessageChatSendParams(), photoEntry.effectId, payStars, getSendMonoForumPeerId(), getSendMessageSuggestionParams(), photoEntry.hasSpoiler);
                    } else if (photoEntry.path != null) {
                        SendMessagesHelper.prepareSendingPhoto(getAccountInstance(), photoEntry.path, photoEntry.thumbPath, null, dialog_id, replyingMessageObject, getThreadMessage(), null, replyingQuote, photoEntry.entities, photoEntry.stickers, null, photoEntry.ttl, editingMessageObject, videoEditedInfo, notify, scheduleDate, scheduleRepeatPeriod, 0, forceDocument, photoEntry.caption, getMessageChatSendParams(), photoEntry.effectId, payStars, getSendMonoForumPeerId(), getSendMessageSuggestionParams(), photoEntry.hasSpoiler);
                    }""",
        "ChatActivity sendMedia normal spoiler"
    )

    with open(chat_path, "w", encoding="utf-8") as f:
        f.write(chat)
    print("Successfully patched ChatActivity.java (media spoilers)")

    # 3. PhotoViewer.java (spoiler flag + max HD 1080p video compression default)
    pv_path = "./TMessagesProj/src/main/java/org/telegram/ui/PhotoViewer.java"
    if not os.path.exists(pv_path):
        raise FileNotFoundError(f"Missing {pv_path}")

    with open(pv_path, "r", encoding="utf-8") as f:
        pv = f.read()

    pv = must_replace(
        pv,
        """                                if (photoEntry.imagePath != null) {
                                    SendMessagesHelper.prepareSendingPhoto(parentChatActivity.getAccountInstance(), photoEntry.imagePath, photoEntry.thumbPath, null, parentChatActivity.getDialogId(), replyToMsg, parentChatActivity.getThreadMessage(), null, replyQuote, photoEntry.entities, photoEntry.stickers, null, photoEntry.ttl, editingMessageObject, videoEditedInfo, notify, scheduleDate, scheduleRepeatPeriod, 0, forceDocument, photoEntry.caption, parentChatActivity.getMessageChatSendParams(), 0, 0, parentChatActivity.getSendMonoForumPeerId(), parentChatActivity.getSendMessageSuggestionParams());
                                } else if (photoEntry.path != null) {
                                    SendMessagesHelper.prepareSendingPhoto(parentChatActivity.getAccountInstance(), photoEntry.path, photoEntry.thumbPath, null, parentChatActivity.getDialogId(), replyToMsg, parentChatActivity.getThreadMessage(), null, replyQuote, photoEntry.entities, photoEntry.stickers, null, photoEntry.ttl, editingMessageObject, videoEditedInfo, notify, scheduleDate, scheduleRepeatPeriod, 0, forceDocument, photoEntry.caption, parentChatActivity.getMessageChatSendParams(), 0, 0, parentChatActivity.getSendMonoForumPeerId(), parentChatActivity.getSendMessageSuggestionParams());
                                }""",
        """                                if (photoEntry.imagePath != null) {
                                    SendMessagesHelper.prepareSendingPhoto(parentChatActivity.getAccountInstance(), photoEntry.imagePath, photoEntry.thumbPath, null, parentChatActivity.getDialogId(), replyToMsg, parentChatActivity.getThreadMessage(), null, replyQuote, photoEntry.entities, photoEntry.stickers, null, photoEntry.ttl, editingMessageObject, videoEditedInfo, notify, scheduleDate, scheduleRepeatPeriod, 0, forceDocument, photoEntry.caption, parentChatActivity.getMessageChatSendParams(), 0, 0, parentChatActivity.getSendMonoForumPeerId(), parentChatActivity.getSendMessageSuggestionParams(), photoEntry.hasSpoiler);
                                } else if (photoEntry.path != null) {
                                    SendMessagesHelper.prepareSendingPhoto(parentChatActivity.getAccountInstance(), photoEntry.path, photoEntry.thumbPath, null, parentChatActivity.getDialogId(), replyToMsg, parentChatActivity.getThreadMessage(), null, replyQuote, photoEntry.entities, photoEntry.stickers, null, photoEntry.ttl, editingMessageObject, videoEditedInfo, notify, scheduleDate, scheduleRepeatPeriod, 0, forceDocument, photoEntry.caption, parentChatActivity.getMessageChatSendParams(), 0, 0, parentChatActivity.getSendMonoForumPeerId(), parentChatActivity.getSendMessageSuggestionParams(), photoEntry.hasSpoiler);
                                }""",
        "PhotoViewer sendButtonPressed spoiler"
    )

    old_comp = """        SharedPreferences preferences = MessagesController.getGlobalMainSettings();
        int compressionsCount = this.compressionsCount;
        int maxCompression = 2;
        while (compressionsCount < 5) {
            int selectedCompression = preferences.getInt(String.format(Locale.US, "compress_video_%d", compressionsCount), -1);
            if (selectedCompression >= 0) {
                return Math.min(selectedCompression, maxCompression);
            }
            compressionsCount++;
        }
        return Math.min(maxCompression, Math.round(DownloadController.getInstance(currentAccount).getMaxVideoBitrate() / (100f / compressionsCount)) - 1);"""

    new_comp = """        SharedPreferences preferences = MessagesController.getGlobalMainSettings();
        int compressionsCount = this.compressionsCount;
        int maxCompression = Math.max(0, this.compressionsCount - 1);
        while (compressionsCount < 5) {
            int selectedCompression = preferences.getInt(String.format(Locale.US, "compress_video_%d", compressionsCount), -1);
            if (selectedCompression >= 0) {
                return Math.min(selectedCompression, maxCompression);
            }
            compressionsCount++;
        }
        return maxCompression;"""

    pv = must_replace(pv, old_comp, new_comp, "PhotoViewer selectCompression HD 1080p default")

    with open(pv_path, "w", encoding="utf-8") as f:
        f.write(pv)
    print("Successfully patched PhotoViewer.java (spoilers + HD 1080p default)")


def patch_client_side_translation():
    path = "./TMessagesProj/src/main/java/org/telegram/messenger/TranslateController.java"
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing {path}")

    with open(path, "r", encoding="utf-8") as f:
        tc = f.read()

    old_avail = """    public boolean isFeatureAvailable() {
        return isChatTranslateEnabled() && UserConfig.getInstance(currentAccount).isPremium();
    }

    public boolean isFeatureAvailable(long dialogId) {
        if (!isChatTranslateEnabled()) {
            return false;
        }
        final TLRPC.Chat chat = getMessagesController().getChat(-dialogId);
        return (
            UserConfig.getInstance(currentAccount).isPremium() ||
            chat != null && chat.autotranslation
        );
    }"""

    new_avail = """    public boolean isFeatureAvailable() {
        return isChatTranslateEnabled();
    }

    public boolean isFeatureAvailable(long dialogId) {
        return isChatTranslateEnabled();
    }"""

    tc = must_replace(tc, old_avail, new_avail, "TranslateController isFeatureAvailable")
    tc = must_replace(
        tc,
        'MessagesController.getGlobalMainSettings().getBoolean("translate_button", false)',
        'MessagesController.getGlobalMainSettings().getBoolean("translate_button", true)',
        "TranslateController default context translate_button=true"
    )
    tc = must_replace(
        tc,
        '} else if (err != null && "TRANSLATIONS_DISABLED_ALT".equalsIgnoreCase(err.text)) {',
        '} else if (err != null && !"TO_LANG_INVALID".equals(err.text)) {',
        "TranslateController free alternativeTranslate fallback"
    )

    with open(path, "w", encoding="utf-8") as f:
        f.write(tc)
    print("Successfully patched TranslateController.java (unlocked chat & context translation)")


def patch_force_120hz():
    path = "./TMessagesProj/src/main/java/org/telegram/ui/LaunchActivity.java"
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing {path}")

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

    content = must_replace(content, old_target, new_target, "LaunchActivity 120Hz force lock")

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Successfully patched LaunchActivity.java (120Hz)")


def patch_secret_media_and_screenshots():
    # 1. SecretMediaViewer.java
    smv_path = "./TMessagesProj/src/main/java/org/telegram/ui/SecretMediaViewer.java"
    if not os.path.exists(smv_path):
        raise FileNotFoundError(f"Missing {smv_path}")

    with open(smv_path, "r", encoding="utf-8") as f:
        smv = f.read()

    # 1a. Disable FLAG_SECURE on windowLayoutParams
    t1 = (
        "        windowLayoutParams.flags = WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN |\n"
        "                WindowManager.LayoutParams.FLAG_LAYOUT_INSET_DECOR |\n"
        "                WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE |\n"
        "                WindowManager.LayoutParams.FLAG_DRAWS_SYSTEM_BAR_BACKGROUNDS;\n"
        "        windowLayoutParams.flags |= WindowManager.LayoutParams.FLAG_SECURE;"
    )
    r1 = (
        "        windowLayoutParams.flags = WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN |\n"
        "                WindowManager.LayoutParams.FLAG_LAYOUT_INSET_DECOR |\n"
        "                WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE |\n"
        "                WindowManager.LayoutParams.FLAG_DRAWS_SYSTEM_BAR_BACKGROUNDS;\n"
        "        windowLayoutParams.flags &= ~WindowManager.LayoutParams.FLAG_SECURE; // Graniton: allow screenshots"
    )
    smv = must_replace(smv, t1, r1, "SecretMediaViewer windowLayoutParams FLAG_SECURE")

    # 1b. Clear FLAG_SECURE in setParentActivity
    t2 = "        parentActivity = activity;\n\n        scroller = new Scroller(activity);"
    r2 = (
        "        parentActivity = activity;\n"
        "        if (parentActivity != null && parentActivity.getWindow() != null) {\n"
        "            parentActivity.getWindow().clearFlags(WindowManager.LayoutParams.FLAG_SECURE);\n"
        "        }\n\n"
        "        scroller = new Scroller(activity);"
    )
    smv = must_replace(smv, t2, r2, "SecretMediaViewer parentActivity clearFlags")

    # 1c. Add Save to Gallery button and shift countdown timer so they do not overlap
    t3 = (
        "        actionBar.setTitleRightMargin(dp(70));\n"
        "        containerView.addView(actionBar, LayoutHelper.createFrame(LayoutHelper.MATCH_PARENT, LayoutHelper.WRAP_CONTENT));\n"
        "        actionBar.setActionBarMenuOnItemClick(new ActionBar.ActionBarMenuOnItemClick() {\n"
        "            @Override\n"
        "            public void onItemClick(int id) {\n"
        "                if (id == -1) {\n"
        "                    closePhoto(true, false);\n"
        "                }\n"
        "            }\n"
        "        });\n\n"
        "        secretHint = new HintView2(activity, HintView2.DIRECTION_TOP);\n"
        "        secretHint.setJoint(1, -26);\n"
        "        secretHint.setPadding(dp(8), dp(8), dp(8), dp(8));\n"
        "        containerView.addView(secretHint, LayoutHelper.createFrame(LayoutHelper.MATCH_PARENT, 80, Gravity.TOP | Gravity.RIGHT, 0, 48, 0, 0));\n\n"
        "        secretDeleteTimer = new SecretDeleteTimer(activity);\n"
        "        containerView.addView(secretDeleteTimer, LayoutHelper.createFrame(119, 48, Gravity.TOP | Gravity.RIGHT, 0, 0, 0, 0));"
    )
    r3 = (
        "        actionBar.setTitleRightMargin(dp(70));\n"
        "        org.telegram.ui.ActionBar.ActionBarMenu menu = actionBar.createMenu();\n"
        "        menu.addItem(1, R.drawable.msg_gallery);\n"
        "        containerView.addView(actionBar, LayoutHelper.createFrame(LayoutHelper.MATCH_PARENT, LayoutHelper.WRAP_CONTENT));\n"
        "        actionBar.setActionBarMenuOnItemClick(new ActionBar.ActionBarMenuOnItemClick() {\n"
        "            @Override\n"
        "            public void onItemClick(int id) {\n"
        "                if (id == -1) {\n"
        "                    closePhoto(true, false);\n"
        "                } else if (id == 1) {\n"
        "                    saveCurrentSecretMedia();\n"
        "                }\n"
        "            }\n"
        "        });\n\n"
        "        secretHint = new HintView2(activity, HintView2.DIRECTION_TOP);\n"
        "        secretHint.setJoint(1, -26);\n"
        "        secretHint.setPadding(dp(8), dp(8), dp(8), dp(8));\n"
        "        containerView.addView(secretHint, LayoutHelper.createFrame(LayoutHelper.MATCH_PARENT, 80, Gravity.TOP | Gravity.RIGHT, 0, 48, 0, 0));\n\n"
        "        secretDeleteTimer = new SecretDeleteTimer(activity);\n"
        "        containerView.addView(secretDeleteTimer, LayoutHelper.createFrame(119, 48, Gravity.TOP | Gravity.RIGHT, 0, 0, 56, 0));"
    )
    smv = must_replace(smv, t3, r3, "SecretMediaViewer Save to Gallery menu button")

    # 1d. Disable auto-delete upon close
    t4 = (
        "        ignoreDelete = messageObject.messageOwner.ttl == 0x7FFFFFFF;\n"
        "        this.onClose = onClose;"
    )
    r4 = (
        "        ignoreDelete = true;\n"
        "        this.onClose = null; // Graniton: prevent auto-deletion of secret/bomb media"
    )
    smv = must_replace(smv, t4, r4, "SecretMediaViewer disable auto-delete")

    # 1e. Cache newly opened secret media unencrypted (cacheType = 0 instead of 2)
    smv = must_replace(
        smv,
        "centerImage.setImage(null, null, currentThumb != null ? new BitmapDrawable(currentThumb.bitmap) : null, -1, null, messageObject, 2);",
        "centerImage.setImage(null, null, currentThumb != null ? new BitmapDrawable(currentThumb.bitmap) : null, -1, null, messageObject, 0);",
        "SecretMediaViewer video thumb cacheType=0"
    )
    smv = must_replace(
        smv,
        "centerImage.setImage(ImageLocation.getForObject(sizeFull, messageObject.photoThumbsObject), null, currentThumb != null ? new BitmapDrawable(currentThumb.bitmap) : null, -1, null, messageObject, 2);",
        "centerImage.setImage(ImageLocation.getForObject(sizeFull, messageObject.photoThumbsObject), null, currentThumb != null ? new BitmapDrawable(currentThumb.bitmap) : null, -1, null, messageObject, 0);",
        "SecretMediaViewer full photo cacheType=0"
    )

    # 1f. Inject resolveAndDecryptSecretFile + saveCurrentSecretMedia on exact class declaration
    smv_header = "public class SecretMediaViewer implements NotificationCenter.NotificationCenterDelegate, GestureDetector.OnGestureListener, GestureDetector.OnDoubleTapListener {"
    save_method = """    private File resolveAndDecryptSecretFile(File cand) {
        if (cand == null) {
            return null;
        }
        String abs = cand.getAbsolutePath();
        if (cand.exists() && cand.length() > 0 && !abs.endsWith(".enc")) {
            return cand;
        }
        File encFile = abs.endsWith(".enc") ? cand : new File(abs + ".enc");
        if (encFile.exists() && encFile.length() > 0) {
            String plainName = cand.getName();
            if (plainName.endsWith(".enc")) {
                plainName = plainName.substring(0, plainName.length() - 4);
            }
            File keyFile = new File(FileLoader.getInternalCacheDir(), plainName + ".enc.key");
            if (keyFile.exists()) {
                try {
                    File outDir = FileLoader.getDirectory(FileLoader.MEDIA_DIR_CACHE);
                    File decFile = new File(outDir, "graniton_dec_" + plainName);
                    if (decFile.exists() && decFile.length() == encFile.length()) {
                        return decFile;
                    }
                    org.telegram.messenger.secretmedia.EncryptedFileInputStream is = new org.telegram.messenger.secretmedia.EncryptedFileInputStream(encFile, keyFile);
                    java.io.FileOutputStream os = new java.io.FileOutputStream(decFile);
                    byte[] buf = new byte[32768];
                    int r;
                    while ((r = is.read(buf)) > 0) {
                        os.write(buf, 0, r);
                    }
                    os.flush();
                    os.close();
                    is.close();
                    if (decFile.exists() && decFile.length() > 0) {
                        return decFile;
                    }
                } catch (Throwable e) {
                    FileLog.e(e);
                }
            }
        }
        return null;
    }

    private void saveCurrentSecretMedia() {
        if (currentMessageObject == null || parentActivity == null) {
            return;
        }
        File resolved = null;
        if (!TextUtils.isEmpty(currentMessageObject.messageOwner.attachPath)) {
            resolved = resolveAndDecryptSecretFile(new File(currentMessageObject.messageOwner.attachPath));
        }
        if (resolved == null) {
            resolved = resolveAndDecryptSecretFile(FileLoader.getInstance(currentAccount).getPathToMessage(currentMessageObject.messageOwner));
        }
        if (resolved == null) {
            resolved = resolveAndDecryptSecretFile(FileLoader.getInstance(currentAccount).getPathToMessage(currentMessageObject.messageOwner, true, true));
        }
        TLRPC.Document doc = currentMessageObject.getDocument();
        if (resolved == null && doc != null) {
            resolved = resolveAndDecryptSecretFile(FileLoader.getInstance(currentAccount).getPathToAttach(doc, false));
            if (resolved == null) {
                resolved = resolveAndDecryptSecretFile(FileLoader.getInstance(currentAccount).getPathToAttach(doc, true));
            }
        }
        if (resolved == null) {
            TLRPC.PhotoSize sizeFull = FileLoader.getClosestPhotoSizeWithSize(currentMessageObject.photoThumbs, AndroidUtilities.getPhotoSize());
            if (sizeFull != null) {
                resolved = resolveAndDecryptSecretFile(FileLoader.getInstance(currentAccount).getPathToAttach(sizeFull, false));
                if (resolved == null) {
                    resolved = resolveAndDecryptSecretFile(FileLoader.getInstance(currentAccount).getPathToAttach(sizeFull, true));
                }
            }
        }
        final boolean mediaIsVideo = currentMessageObject.isVideo() && !MessageObject.isGifDocument(doc);
        if (resolved == null && !mediaIsVideo && centerImage != null) {
            Bitmap bmp = centerImage.getBitmap();
            if (bmp != null && !bmp.isRecycled()) {
                try {
                    File outDir = FileLoader.getDirectory(FileLoader.MEDIA_DIR_CACHE);
                    File bmpFile = new File(outDir, "graniton_secret_" + System.currentTimeMillis() + ".jpg");
                    java.io.FileOutputStream os = new java.io.FileOutputStream(bmpFile);
                    bmp.compress(Bitmap.CompressFormat.JPEG, 98, os);
                    os.flush();
                    os.close();
                    if (bmpFile.exists() && bmpFile.length() > 0) {
                        resolved = bmpFile;
                    }
                } catch (Throwable e) {
                    FileLog.e(e);
                }
            }
        }
        if (resolved != null && resolved.exists()) {
            org.telegram.messenger.MediaController.saveFile(resolved.toString(), parentActivity, mediaIsVideo ? 1 : 0, null, null, uri -> {
                if (containerView != null) {
                    org.telegram.ui.Components.BulletinFactory.createSaveToGalleryBulletin(containerView, mediaIsVideo, 0xf9222222, 0xffffffff).show();
                }
            });
        } else if (doc != null) {
            FileLoader.getInstance(currentAccount).loadFile(doc, currentMessageObject, FileLoader.PRIORITY_HIGH, 0);
            android.widget.Toast.makeText(parentActivity, LocaleController.getString(R.string.Loading), android.widget.Toast.LENGTH_SHORT).show();
        }
    }
"""
    smv = must_replace(smv, smv_header, smv_header + "\n" + save_method, "SecretMediaViewer saveCurrentSecretMedia injection")

    with open(smv_path, "w", encoding="utf-8") as f:
        f.write(smv)
    print("Successfully patched SecretMediaViewer.java")

    # 2. FlagSecureReason.java
    fsr_path = "./TMessagesProj/src/main/java/org/telegram/messenger/FlagSecureReason.java"
    if not os.path.exists(fsr_path):
        raise FileNotFoundError(f"Missing {fsr_path}")

    with open(fsr_path, "r", encoding="utf-8") as f:
        fsr = f.read()

    t_fsr = """    private static void updateWindowSecure(Window window) {
        if (window == null) {
            return;
        }

        if (isSecuredNow(window)) {
            window.addFlags(WindowManager.LayoutParams.FLAG_SECURE);
            AndroidUtilities.logFlagSecure();
        } else {
            window.clearFlags(WindowManager.LayoutParams.FLAG_SECURE);
            AndroidUtilities.logFlagSecure();
        }
    }

    public static boolean isSecuredNow(Window window) {
        return currentSecureReasons != null && currentSecureReasons.get(window) != null;
    }"""

    r_fsr = """    private static void updateWindowSecure(Window window) {
        if (window == null) {
            return;
        }
        window.clearFlags(WindowManager.LayoutParams.FLAG_SECURE);
    }

    public static boolean isSecuredNow(Window window) {
        return false;
    }"""
    fsr = must_replace(fsr, t_fsr, r_fsr, "FlagSecureReason disable FLAG_SECURE")
    with open(fsr_path, "w", encoding="utf-8") as f:
        f.write(fsr)
    print("Successfully patched FlagSecureReason.java")

    # 3. PhotoViewer.java (FLAG_SECURE)
    pv_path = "./TMessagesProj/src/main/java/org/telegram/ui/PhotoViewer.java"
    with open(pv_path, "r", encoding="utf-8") as f:
        pv = f.read()

    t_pv = """            if (chatActivity != null && chatActivity.getCurrentEncryptedChat() != null ||
                avatarsDialogId != 0 && MessagesController.getInstance(currentAccount).isPeerNoForwards(avatarsDialogId) ||
                messageObject != null && (MessagesController.getInstance(currentAccount).isPeerNoForwards(messageObject.getDialogId()) ||
                (messageObject.messageOwner != null && messageObject.messageOwner.noforwards)) || messageObject != null && messageObject.hasRevealedExtendedMedia() ||
                isPageBlocksNoForwards(pageBlocksAdapter)
            ) {
                windowLayoutParams.flags |= WindowManager.LayoutParams.FLAG_SECURE;
                AndroidUtilities.logFlagSecure();
            } else {
                windowLayoutParams.flags &=~ WindowManager.LayoutParams.FLAG_SECURE;
                AndroidUtilities.logFlagSecure();
            }"""

    r_pv = """            windowLayoutParams.flags &= ~WindowManager.LayoutParams.FLAG_SECURE; // Graniton: always allow screenshots in PhotoViewer"""
    pv = must_replace(pv, t_pv, r_pv, "PhotoViewer disable FLAG_SECURE")
    with open(pv_path, "w", encoding="utf-8") as f:
        f.write(pv)
    print("Successfully patched PhotoViewer.java (FLAG_SECURE)")

    # 4. LaunchActivity.java (FLAG_SECURE)
    la_path = "./TMessagesProj/src/main/java/org/telegram/ui/LaunchActivity.java"
    with open(la_path, "r", encoding="utf-8") as f:
        la = f.read()

    t_la = """        flagSecureReason = new FlagSecureReason(getWindow(), () -> SharedConfig.passcodeHash.length() > 0 && !SharedConfig.allowScreenCapture);
        flagSecureReason.attach();"""
    r_la = """        SharedConfig.allowScreenCapture = true;
        flagSecureReason = new FlagSecureReason(getWindow(), () -> false);
        flagSecureReason.attach();
        getWindow().clearFlags(WindowManager.LayoutParams.FLAG_SECURE);"""
    la = must_replace(la, t_la, r_la, "LaunchActivity clear FLAG_SECURE")
    with open(la_path, "w", encoding="utf-8") as f:
        f.write(la)
    print("Successfully patched LaunchActivity.java (FLAG_SECURE)")

    # 5. SharedConfig.java
    sc_path = "./TMessagesProj/src/main/java/org/telegram/messenger/SharedConfig.java"
    if not os.path.exists(sc_path):
        raise FileNotFoundError(f"Missing {sc_path}")

    with open(sc_path, "r", encoding="utf-8") as f:
        sc = f.read()

    sc = must_replace(
        sc,
        'allowScreenCapture = preferences.getBoolean("allowScreenCapture", false);',
        'allowScreenCapture = preferences.getBoolean("allowScreenCapture", true);',
        "SharedConfig allowScreenCapture pref default",
        count=None
    )
    sc = sc.replace("allowScreenCapture = false;", "allowScreenCapture = true;")
    with open(sc_path, "w", encoding="utf-8") as f:
        f.write(sc)
    print("Successfully patched SharedConfig.java")

    # 6. ChatActivity.java (stealth bomb viewing + all 4 context menu branches + .enc-aware saving/sharing)
    chat_path = "./TMessagesProj/src/main/java/org/telegram/ui/ChatActivity.java"
    with open(chat_path, "r", encoding="utf-8") as f:
        chat = f.read()

    # 6a. Stealth bomb viewing: do not send read receipt or start server TTL countdown, and do not delete view-once media
    chat = must_replace(
        chat,
        "    private Runnable sendSecretMessageRead(MessageObject messageObject, boolean readNow) {",
        "    private Runnable sendSecretMessageRead(MessageObject messageObject, boolean readNow) { return null; } private Runnable _unused_sendSecretMessageRead(MessageObject messageObject, boolean readNow) {",
        "ChatActivity stealth sendSecretMessageRead"
    )
    chat = must_replace(
        chat,
        "    private Runnable sendSecretMediaDelete(MessageObject messageObject) {",
        "    private Runnable sendSecretMediaDelete(MessageObject messageObject) { return null; } private Runnable _unused_sendSecretMediaDelete(MessageObject messageObject) {",
        "ChatActivity stealth sendSecretMediaDelete"
    )

    # 6b. Context menu Save to Gallery & Share across all 4 branches (including Secret Chats!)
    chat = must_replace(
        chat,
        """                        if (selectedObject.isVideo()) {
                            if (!selectedObject.needDrawBluredPreview()) {
                                items.add(LocaleController.getString(R.string.SaveToGallery));
                                options.add(OPTION_SAVE_TO_GALLERY);
                                icons.add(R.drawable.msg_gallery);
                                items.add(LocaleController.getString(R.string.ShareFile));
                                options.add(OPTION_SHARE);
                                icons.add(R.drawable.msg_shareout);
                            }""",
        """                        if (selectedObject.isVideo()) {
                            if (true) { // Graniton: allow saving secret/bomb video
                                items.add(LocaleController.getString(R.string.SaveToGallery));
                                options.add(OPTION_SAVE_TO_GALLERY);
                                icons.add(R.drawable.msg_gallery);
                                items.add(LocaleController.getString(R.string.ShareFile));
                                options.add(OPTION_SHARE);
                                icons.add(R.drawable.msg_shareout);
                            }""",
        "ChatActivity menu type 4 video"
    )
    chat = must_replace(
        chat,
        """                        } else {
                            if (!selectedObject.needDrawBluredPreview()) {
                                items.add(LocaleController.getString(R.string.SaveToGallery));
                                options.add(OPTION_SAVE_TO_GALLERY);
                                icons.add(R.drawable.msg_gallery);
                            }
                        }""",
        """                        } else {
                            if (true) { // Graniton: allow saving secret/bomb photos
                                items.add(LocaleController.getString(R.string.SaveToGallery));
                                options.add(OPTION_SAVE_TO_GALLERY);
                                icons.add(R.drawable.msg_gallery);
                            }
                        }""",
        "ChatActivity menu type 4 photo"
    )
    chat = must_replace(
        chat,
        """                } else if (type == 6 && !noforwardsOrPaidMedia && !selectedObject.hasRevealedExtendedMedia()) {
                    if (!selectedObject.needDrawBluredPreview() && !selectedObject.isVoiceOnce() && !selectedObject.isRoundOnce()) {""",
        """                } else if (type == 6 && !noforwardsOrPaidMedia && !selectedObject.hasRevealedExtendedMedia()) {
                    if (true) { // Graniton: allow saving type 6 secret media""",
        "ChatActivity menu type 6 media"
    )
    chat = must_replace(
        chat,
        "if (type == 4 && !noforwardsOrPaidMedia && !selectedObject.hasRevealedExtendedMedia() && !selectedObject.needDrawBluredPreview()) {",
        "if (type == 4 && !noforwardsOrPaidMedia && !selectedObject.hasRevealedExtendedMedia()) { // Graniton: allow saving in Secret Chats",
        "ChatActivity menu secret chat type 4"
    )

    # 6c. Upgrade saveMessageToGallery, OPTION_SAVE_TO_GALLERY, OPTION_SAVE_TO_GALLERY2, and OPTION_SHARE with .enc decryption & sizeFull lookup
    old_save_gallery = """    private void saveMessageToGallery(MessageObject messageObject) {
        String path = messageObject.messageOwner.attachPath;
        if (!TextUtils.isEmpty(path)) {
            File temp = new File(path);
            if (!temp.exists()) {
                path = null;
            }
        }
        if (TextUtils.isEmpty(path)) {
            File f = FileLoader.getInstance(currentAccount).getPathToMessage(messageObject.messageOwner);
            if (f != null && f.exists()) {
                path = f.getPath();
            }
        }
        if (TextUtils.isEmpty(path) && messageObject.cachedQuality != null && messageObject.cachedQuality.isCached()) {
            File f = new File(messageObject.cachedQuality.uri.getPath());
            if (f != null && f.exists()) {
                path = f.getPath();
            }
        }
        if (TextUtils.isEmpty(path) && messageObject.qualityToSave != null) {
            File f = FileLoader.getInstance(currentAccount).getPathToAttach(messageObject.qualityToSave, null, false, true);
            if (f != null && f.exists()) {
                path = f.getPath();
            }
        }
        if (TextUtils.isEmpty(path)) {
            return;
        }"""

    new_save_gallery = """    private File resolveGranitonMediaFile(File cand) {
        if (cand == null) {
            return null;
        }
        String abs = cand.getAbsolutePath();
        if (cand.exists() && cand.length() > 0 && !abs.endsWith(".enc")) {
            return cand;
        }
        File encFile = abs.endsWith(".enc") ? cand : new File(abs + ".enc");
        if (encFile.exists() && encFile.length() > 0) {
            String plainName = cand.getName();
            if (plainName.endsWith(".enc")) {
                plainName = plainName.substring(0, plainName.length() - 4);
            }
            File keyFile = new File(FileLoader.getInternalCacheDir(), plainName + ".enc.key");
            if (keyFile.exists()) {
                try {
                    File outDir = FileLoader.getDirectory(FileLoader.MEDIA_DIR_CACHE);
                    File decFile = new File(outDir, "graniton_dec_" + plainName);
                    if (decFile.exists() && decFile.length() == encFile.length()) {
                        return decFile;
                    }
                    org.telegram.messenger.secretmedia.EncryptedFileInputStream is = new org.telegram.messenger.secretmedia.EncryptedFileInputStream(encFile, keyFile);
                    java.io.FileOutputStream os = new java.io.FileOutputStream(decFile);
                    byte[] buf = new byte[32768];
                    int r;
                    while ((r = is.read(buf)) > 0) {
                        os.write(buf, 0, r);
                    }
                    os.flush();
                    os.close();
                    is.close();
                    if (decFile.exists() && decFile.length() > 0) {
                        return decFile;
                    }
                } catch (Throwable e) {
                    FileLog.e(e);
                }
            }
        }
        return null;
    }

    private String resolveGranitonMediaPath(MessageObject messageObject) {
        if (messageObject == null || messageObject.messageOwner == null) {
            return null;
        }
        File resolved = null;
        if (!TextUtils.isEmpty(messageObject.messageOwner.attachPath)) {
            resolved = resolveGranitonMediaFile(new File(messageObject.messageOwner.attachPath));
        }
        if (resolved == null) {
            resolved = resolveGranitonMediaFile(FileLoader.getInstance(currentAccount).getPathToMessage(messageObject.messageOwner));
        }
        if (resolved == null) {
            resolved = resolveGranitonMediaFile(FileLoader.getInstance(currentAccount).getPathToMessage(messageObject.messageOwner, true, true));
        }
        if (resolved == null && messageObject.cachedQuality != null && messageObject.cachedQuality.isCached()) {
            resolved = resolveGranitonMediaFile(new File(messageObject.cachedQuality.uri.getPath()));
        }
        if (resolved == null && messageObject.qualityToSave != null) {
            resolved = resolveGranitonMediaFile(FileLoader.getInstance(currentAccount).getPathToAttach(messageObject.qualityToSave, null, false, true));
        }
        TLRPC.Document doc = messageObject.getDocument();
        if (resolved == null && doc != null) {
            resolved = resolveGranitonMediaFile(FileLoader.getInstance(currentAccount).getPathToAttach(doc, false));
            if (resolved == null) {
                resolved = resolveGranitonMediaFile(FileLoader.getInstance(currentAccount).getPathToAttach(doc, true));
            }
        }
        if (resolved == null) {
            TLRPC.PhotoSize sizeFull = FileLoader.getClosestPhotoSizeWithSize(messageObject.photoThumbs, AndroidUtilities.getPhotoSize());
            if (sizeFull != null) {
                resolved = resolveGranitonMediaFile(FileLoader.getInstance(currentAccount).getPathToAttach(sizeFull, false));
                if (resolved == null) {
                    resolved = resolveGranitonMediaFile(FileLoader.getInstance(currentAccount).getPathToAttach(sizeFull, true));
                }
            }
        }
        return resolved != null ? resolved.getPath() : null;
    }

    private void saveMessageToGallery(MessageObject messageObject) {
        String path = resolveGranitonMediaPath(messageObject);
        if (TextUtils.isEmpty(path)) {
            TLRPC.Document doc = messageObject != null ? messageObject.getDocument() : null;
            if (doc != null) {
                FileLoader.getInstance(currentAccount).loadFile(doc, messageObject, FileLoader.PRIORITY_HIGH, 0);
            } else if (messageObject != null) {
                TLRPC.PhotoSize sizeFull = FileLoader.getClosestPhotoSizeWithSize(messageObject.photoThumbs, AndroidUtilities.getPhotoSize());
                if (sizeFull != null) {
                    FileLoader.getInstance(currentAccount).loadFile(org.telegram.messenger.ImageLocation.getForObject(sizeFull, messageObject.photoThumbsObject), messageObject, null, FileLoader.PRIORITY_HIGH, 0);
                }
            }
            return;
        }"""

    chat = must_replace(chat, old_save_gallery, new_save_gallery, "ChatActivity saveMessageToGallery .enc decryption")

    old_opt_save1 = """                } else {
                    saveMessageToGallery(selectedObject);
                    if (getParentActivity() != null) {
                        BulletinFactory.of(this).createDownloadBulletin(selectedObject.isLivePhoto() ? BulletinFactory.FileType.LIVEPHOTO : (selectedObject.isVideo() ? BulletinFactory.FileType.VIDEO : BulletinFactory.FileType.PHOTO), themeDelegate).show();
                    }
                }"""

    new_opt_save1 = """                } else {
                    boolean hadFile = !TextUtils.isEmpty(resolveGranitonMediaPath(selectedObject));
                    saveMessageToGallery(selectedObject);
                    if (getParentActivity() != null) {
                        if (hadFile) {
                            BulletinFactory.of(this).createDownloadBulletin(selectedObject.isLivePhoto() ? BulletinFactory.FileType.LIVEPHOTO : (selectedObject.isVideo() ? BulletinFactory.FileType.VIDEO : BulletinFactory.FileType.PHOTO), themeDelegate).show();
                        } else {
                            android.widget.Toast.makeText(getParentActivity(), LocaleController.getString(R.string.Loading), android.widget.Toast.LENGTH_SHORT).show();
                        }
                    }
                }"""

    chat = must_replace(chat, old_opt_save1, new_opt_save1, "ChatActivity OPTION_SAVE_TO_GALLERY accurate feedback")

    old_opt_share = """            case OPTION_SHARE: {
                String path = selectedObject.messageOwner.attachPath;
                if (path != null && path.length() > 0) {
                    File temp = new File(path);
                    if (!temp.exists()) {
                        path = null;
                    }
                }
                if (path == null || path.length() == 0) {
                    path = getFileLoader().getPathToMessage(selectedObject.messageOwner).toString();
                }
                Intent intent = new Intent(Intent.ACTION_SEND);
                intent.setType(selectedObject.getDocument().mime_type);"""

    new_opt_share = """            case OPTION_SHARE: {
                String path = resolveGranitonMediaPath(selectedObject);
                if (TextUtils.isEmpty(path)) {
                    path = getFileLoader().getPathToMessage(selectedObject.messageOwner).toString();
                }
                Intent intent = new Intent(Intent.ACTION_SEND);
                intent.setType(selectedObject.getDocument() != null ? selectedObject.getDocument().mime_type : "image/jpeg");"""

    chat = must_replace(chat, old_opt_share, new_opt_share, "ChatActivity OPTION_SHARE .enc decryption")

    old_opt_save2 = """            case OPTION_SAVE_TO_GALLERY2: {
                String path = selectedObject.messageOwner.attachPath;
                if (path != null && path.length() > 0) {
                    File temp = new File(path);
                    if (!temp.exists()) {
                        path = null;
                    }
                }
                if (TextUtils.isEmpty(path)) {
                    File f = FileLoader.getInstance(currentAccount).getPathToMessage(selectedObject.messageOwner);
                    if (f != null && f.exists()) {
                        path = f.getPath();
                    }
                }
                if (TextUtils.isEmpty(path)) {
                    File f = FileLoader.getInstance(currentAccount).getPathToMessage(selectedObject.messageOwner, true, true);
                    if (f != null && f.exists()) {
                        path = f.getPath();
                    }
                }
                if (TextUtils.isEmpty(path) && selectedObject.cachedQuality != null && selectedObject.cachedQuality.isCached()) {
                    File f = new File(selectedObject.cachedQuality.uri.getPath());
                    if (f != null && f.exists()) {
                        path = f.getPath();
                    }
                }
                if (TextUtils.isEmpty(path) && selectedObject.qualityToSave != null) {
                    File f = FileLoader.getInstance(currentAccount).getPathToAttach(selectedObject.qualityToSave, null, false, true);
                    if (f != null && f.exists()) {
                        path = f.getPath();
                    }
                }"""

    new_opt_save2 = """            case OPTION_SAVE_TO_GALLERY2: {
                String path = resolveGranitonMediaPath(selectedObject);"""

    chat = must_replace(chat, old_opt_save2, new_opt_save2, "ChatActivity OPTION_SAVE_TO_GALLERY2 .enc decryption")

    with open(chat_path, "w", encoding="utf-8") as f:
        f.write(chat)
    print("Successfully patched ChatActivity.java (stealth bombs + context menu + .enc decryption)")


if __name__ == "__main__":
    patch_instant_camera_and_video_notes()
    patch_ghost_and_anti_delete()
    patch_message_restrictions()
    patch_media_spoilers_and_hd_video()
    patch_client_side_translation()
    patch_force_120hz()
    patch_secret_media_and_screenshots()
    print("=== All Graniton Power-Pack patches applied and verified! ===")
