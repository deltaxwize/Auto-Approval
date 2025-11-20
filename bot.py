from pyrogram import Client, filters, ContinuePropagation
from pyrogram.types import (
    Message, InlineKeyboardButton, InlineKeyboardMarkup,
    CallbackQuery, ChatJoinRequest
)
from pyrogram.errors import FloodWait, UserNotParticipant, PeerIdInvalid
import asyncio
from urllib.parse import quote
from database import add_user, add_group, all_users, all_groups, users, remove_user
from configs import cfg
import time

# Initialize Bot
app = Client(
    "approver",
    api_id=cfg.API_ID,
    api_hash=cfg.API_HASH,
    bot_token=cfg.BOT_TOKEN
)

# Auto Approve Join Requests
@app.on_chat_join_request((filters.group | filters.channel))
async def auto_approve(client: Client, request: ChatJoinRequest):
    chat = request.chat
    user = request.from_user

    try:
        # Check if bot is admin with invite permission
        me = await client.get_chat_member(chat.id, "me")
        if not me.privileges or not me.privileges.can_invite_users:
            return

        await client.approve_chat_join_request(chat.id, user.id)
        add_group(chat.id)

        # Generate invite link safely
        try:
            invite_link = await client.export_invite_link(chat.id)
        except:
            invite_link = f"https://t.me/{chat.username}" if chat.username else "https://t.me/telegram"

        share_text = f"Join {chat.title}!"
        if chat.description:
            share_text += f"\n\n{chat.description}"

        encoded_text = quote(share_text)
        encoded_link = quote(invite_link)
        share_url = f"https://t.me/share/url?url={encoded_link}&text={encoded_text}"

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Verify To Approve", url=share_url),
                InlineKeyboardButton("Similar Channels", url="https://t.me/autoapprovalprobot?start=start")
            ],
            [
                InlineKeyboardButton("THE PARADISE ISLAND", url="https://t.me/CornParadise")
            ]
        ])

        welcome_msg = (
            f"**Welcome to {chat.title}!**\n\n"
            f"Your request has been approved!\n"
            f"Help us grow by sharing this group!\n\n"
            f"Powered by @ALLHQC"
        )

        await client.send_message(
            chat_id=user.id,
            text=welcome_msg,
            reply_markup=keyboard,
            disable_web_page_preview=True
        )
        add_user(user.id)

    except PeerIdInvalid:
        print(f"[{user.id}] User has not started the bot.")
    except FloodWait as e:
        print(f"FloodWait: Sleeping for {e.value} seconds")
        await asyncio.sleep(e.value)
    except Exception as e:
        print(f"Error in join request: {e}")

# Start Command
@app.on_message(filters.private & filters.command("start"))
async def start(client: Client, message: Message):
    user = message.from_user

    # Force join check
    try:
        await client.get_chat_member(cfg.CHID, user.id)
    except UserNotParticipant:
        try:
            link = await client.export_invite_link(cfg.CHID)
        except:
            link = f"https://t.me/{(await client.get_chat(cfg.CHID)).username}"

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Join Channel", url=link),
                InlineKeyboardButton("Check Again", callback_data="checkjoin")
            ]
        ])

        await message.reply_text(
            "**Access Denied!**\n\n"
            "Please join our update channel first to use this bot.\n"
            "After joining, press 'Check Again'",
            reply_markup=keyboard
        )
        return

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Dark Oracle", url="https://t.me/Oracle_Dark"),
            InlineKeyboardButton("THE PARADISE ISLAND", url="https://t.me/CornParadise")
        ],
        [
            InlineKeyboardButton("ADD ME", url="https://t.me/autoapprovalprobot?startchannel=AdBots&admin=invite_users+manage_chat")
        ],
        [
            InlineKeyboardButton("Contact For Ads", url="https://t.me/awakendheart")
        ]
    ])

    add_user(user.id)
    await message.reply_photo(
        photo="https://graph.org/file/bc6102449fb6da8bf0418-ef1454d0e99fccaadf.jpg",
        caption=(
            f"**Hello {user.mention}!**\n\n"
            "Welcome to **Auto Approve Bot**!\n"
            "I automatically approve join requests in groups & channels.\n\n"
            "Add me as admin with 'Manage Join Requests' permission!\n\n"
            "Powered by @ALLHQC"
        ),
        reply_markup=keyboard
    )

# Check Join Callback
@app.on_callback_query(filters.regex("^checkjoin$"))
async def check_join(client: Client, callback: CallbackQuery):
    try:
        await client.get_chat_member(cfg.CHID, callback.from_user.id)
    except UserNotParticipant:
        await callback.answer("You still haven't joined the channel!", show_alert=True)
        return

    await callback.message.delete()
    await start(client, callback.message)  # Reuse start function
    await callback.answer("Access Granted!")

# Stats Command (Sudo Only)
@app.on_message(filters.command("users") & filters.user(cfg.SUDO))
async def stats(_, message: Message):
    await message.reply_text(
        f"**Bot Stats**\n\n"
        f"Users: `{len(all_users())}`\n"
        f"Groups: `{len(all_groups())}`\n"
        f"Total: `{len(all_users()) + len(all_groups())}`"
    )

# Broadcast (Reply to message)
@app.on_message(filters.command("bcast") & filters.user(cfg.SUDO))
async def broadcast(client: Client, message: Message):
    if not message.reply_to_message:
        await message.reply("Reply to a message to broadcast!")
        return

    users_list = [user["user_id"] async for user in users.find()]
    sent = 0
    failed = 0
    status = await message.reply("Broadcasting...")

    for user_id in users_list:
        try:
            await message.reply_to_message.copy(user_id)
            sent += 1
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except:
            failed += 1
        await status.edit_text(f"Broadcast: {sent} sent | {failed} failed")

    await status.edit_text(f"**Broadcast Completed**\nSent: `{sent}`\nFailed: `{failed}`")

# Forward Cast
@app.on_message(filters.command("fcast") & filters.user(cfg.SUDO))
async def fcast(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply("Reply to a message!")

    users_list = [user["user_id"] async for user in users.find()]
    sent = 0
    status = await message.reply("Forwarding...")

    for user_id in users_list:
        try:
            await message.reply_to_message.forward(user_id)
            sent += 1
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except:
            pass
        if sent % 10 == 0:
            await status.edit_text(f"Forwarded to {sent} users...")

    await status.edit_text(f"**Forward Completed: {sent} users**")

# Run Bot
print("Auto Approve Bot Started!")
app.run()
