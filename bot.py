from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram import filters, Client, errors, enums
from pyrogram.errors import UserNotParticipant
from pyrogram.errors.exceptions.flood_420 import FloodWait
from database import add_user, add_group, all_users, all_groups, users, remove_user
from configs import cfg
import random
import asyncio
from urllib.parse import quote
import uuid

# Initialize the Telegram Client
app = Client(
    name="approver",
    api_id=cfg.API_ID,
    api_hash=cfg.API_HASH,
    bot_token=cfg.BOT_TOKEN
)

# --------------------------------------------- Chat Join Request Handler ---------------------------------------------
@app.on_chat_join_request(filters.group | filters.channel)
async def approve_join_request(_, message: Message):
    """Handle chat join requests for groups and channels."""
    chat = message.chat
    user = message.from_user
    try:
        # Add group to database and approve the join request
        add_group(chat.id)
        await app.approve_chat_join_request(chat.id, user.id)

        # Fetch chat information and create an invite link
        chat_info = await app.get_chat(chat.id)
        invite_link = await app.create_chat_invite_link(chat.id)
        share_text = f"Join {chat_info.title} 🚀"
        encoded_text = quote(share_text)
        encoded_url = quote(invite_link.invite_link)

        # Include chat description if available
        if chat_info.description:
            share_text += f"\n\n{chat_info.description}"

        # Create share URL for Telegram
        share_url = f"https://t.me/share/url?url={encoded_url}&text={encoded_text}"

        # Inline keyboard with specified buttons
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🌟 𝐕𝐞𝐫𝐢𝐟𝐲 𝐓𝐨 𝐀𝐩𝐩𝐫𝐨𝐯𝐞", url=share_url),
                InlineKeyboardButton("📢 𝐒𝐢𝐦𝐢𝐥𝐚𝐫 𝐂𝐡𝐚𝐧𝐧𝐞𝐥𝐬", url="https://t.me/autoapprovalprobot?start=start")
            ],
            [
                InlineKeyboardButton("💬𝐓ɦ� �α�αᑯ��� ��ᥣα𐓣ᑯ", url="https://t.me/CornParadise")
            ]
        ])

        # Send welcome message to user's DM
        await app.send_message(
            user.id,
            f"🎉 **Welcome to {chat.title}!** 🎉\n\n"
            f"Your request to join has been approved! 🙌\n"
            f"Help us grow by sharing this group with your friends! 🌐\n\n"
            f"__Powered by @ALLHQC__",
            reply_markup=keyboard
        )
        add_user(user.id)

    except errors.PeerIdInvalid:
        print("User hasn't started the bot or isn't part of the group.")
    except Exception as err:
        print(f"Error: {str(err)}")

# --------------------------------------------- Start Command Handler ---------------------------------------------
@app.on_message(filters.private & filters.command("start"))
async def start_command(_, message: Message):
    """Handle the /start command in private chats."""
    user = message.from_user
    try:
        # Check if user is a member of the update channel
        await app.get_chat_member(cfg.CHID, user.id)
    except UserNotParticipant:
        try:
            # Generate invite link for the update channel
            invite_link = await app.create_chat_invite_link(int(cfg.CHID))
        except Exception:
            await message.reply("⚠️ **Error:** Please ensure I am an admin in your channel!")
            return

        # Create inline keyboard for channel join
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📣 Join Channel", url=invite_link.invite_link),
                InlineKeyboardButton("🔄 Check Again", callback_data="chk")
            ]
        ])
        await message.reply_text(
            "🚫 **Access Denied!**\n\n"
            "To use this bot, please join our update channel first. "
            "Once joined, click 'Check Again' to proceed! 🔐",
            reply_markup=keyboard
        )
        return

    # Welcome message with enhanced design
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📢 𝐃α𝗋𝗄 𝐎𝗋α𝖼ᥣ𝖾", url="https://t.me/Oracle_Dark"),
            InlineKeyboardButton("💬 𝐓ɦ� �α�αᑯ��� ��ᥣα𐓣ᑯ ", url="https://t.me/CornParadise")
        ],
        [
                InlineKeyboardButton("➕𝗔𝗗𝗗 𝗠𝗘 ➕", url="https://t.me/autoapprovalprobot?startchannel=AdBots&admin=invite_users+manage_chat")
            ],
        [
            InlineKeyboardButton("🌐 Cᴏɴᴛᴀᴄᴛ Fᴏʀ Aᴅs", url="https://t.me/awakendheart")
        ]
    ])

    add_user(user.id)
    await message.reply_photo(
        photo="https://graph.org/file/bc6102449fb6da8bf0418-ef1454d0e99fccaadf.jpg",
        caption=(
            f"👋 **Hello {user.mention}!** 👋\n\n"
            f"Welcome to the **Auto Approve Bot**! 🤖\n"
            f"I automatically approve join requests for groups and channels. "
            f"Add me to your chat and grant me admin permissions to manage members! 🚀\n\n"
            f"__Powered by @ALLHQC__"
        ),
        reply_markup=keyboard
    )

# --------------------------------------------- Callback Query Handler ---------------------------------------------
@app.on_callback_query(filters.regex("chk"))
async def check_channel_membership(_, callback: CallbackQuery):
    """Handle callback queries for checking channel membership."""
    user = callback.from_user
    try:
        await app.get_chat_member(cfg.CHID, user.id)
    except UserNotParticipant:
        await callback.answer(
            "🚫 You haven't joined the update channel yet. Please join and try again! 🚫",
            show_alert=True
        )
        return

    # Welcome message after successful channel join
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📢 𝐓𝐡𝐄 𝐄𝐓𝐇𝐀𝐍𝐒", url="https://t.me/The_Ethans"),
            InlineKeyboardButton("💬 𝐓ɦ� �α�αᑯ��� ��ᥣα𐓣ᑯ", url="https://t.me/CornParadise")
        ],
        [        InlineKeyboardButton("➕𝗔𝗗𝗗 𝗠𝗘 ➕", url="https://t.me/autoapprovalprobot?startchannel=AdBots&admin=invite_users+manage_chat")
            ],
        [
            InlineKeyboardButton("🌐 Cᴏɴᴛᴀᴄᴛ Fᴏʀ Aᴅs", url="https://t.me/awakendheart")
        ]
    ])

    add_user(user.id)
    await callback.message.edit_text(
        text=(
            f"🎉 **Welcome {user.mention}!** 🎉\n\n"
            f"I'm the **Auto Approve Bot**! 🤖\n"
            f"I handle join requests for groups and channels automatically. "
            f"Add me to your chat and make me an admin with member management permissions! 🚀\n\n"
            f"__Powered by @ALLHQC__"
        ),
        reply_markup=keyboard
    )

# --------------------------------------------- User and Group Stats Handler ---------------------------------------------
@app.on_message(filters.command("users") & filters.user(cfg.SUDO))
async def stats_command(_, message: Message):
    """Display statistics about users and groups."""
    total_users = all_users()
    total_groups = all_groups()
    total_chats = total_users + total_groups

    await message.reply_text(
        f"📊 **Chat Statistics** 📊\n\n"
        f"🙋‍♂️ **Users**: `{total_users}`\n"
        f"👥 **Groups**: `{total_groups}`\n"
        f"🌐 **Total Chats**: `{total_chats}`"
    )

# --------------------------------------------- Broadcast Message Handler ---------------------------------------------
@app.on_message(filters.command("bcast") & filters.user(cfg.SUDO))
async def broadcast_message(_, message: Message):
    """Broadcast a message to all users."""
    all_users = users
    status_message = await message.reply_text("⚡ **Processing Broadcast...**")
    success = 0
    failed = 0
    deactivated = 0
    blocked = 0

    for user in all_users.find():
        try:
            user_id = user["user_id"]
            await message.reply_to_message.copy(int(user_id))
            success += 1
        except FloodWait as ex:
            await asyncio.sleep(ex.value)
            await message.reply_to_message.copy(int(user_id))
        except errors.InputUserDeactivated:
            deactivated += 1
            remove_user(user_id)
        except errors.UserIsBlocked:
            blocked += 1
        except Exception as e:
            print(f"Broadcast error: {e}")
            failed += 1

    await status_message.edit(
        f"📢 **Broadcast Report** 📢\n\n"
        f"✅ **Successful**: `{success}` users\n"
        f"❌ **Failed**: `{failed}` users\n"
        f"🚫 **Blocked**: `{blocked}` users\n"
        f"👻 **Deactivated**: `{deactivated}` users"
    )

# --------------------------------------------- Broadcast Forward Handler ---------------------------------------------
@app.on_message(filters.command("fcast") & filters.user(cfg.SUDO))
async def forward_broadcast(_, message: Message):
    """Forward a message to all users."""
    all_users = users
    status_message = await message.reply_text("⚡ **Processing Forward...**")
    success = 0
    failed = 0
    deactivated = 0
    blocked = 0

    for user in all_users.find():
        try:
            user_id = user["user_id"]
            await message.reply_to_message.forward(int(user_id))
            success += 1
        except FloodWait as ex:
            await asyncio.sleep(ex.value)
            await message.reply_to_message.forward(int(user_id))
        except errors.InputUserDeactivated:
            deactivated += 1
            remove_user(user_id)
        except errors.UserIsBlocked:
            blocked += 1
        except Exception as e:
            print(f"Forward error: {e}")
            failed += 1

    await status_message.edit(
        f"📢 **Forward Report** 📢\n\n"
        f"✅ **Successful**: `{success}` users\n"
        f"❌ **Failed**: `{failed}` users\n"
        f"🚫 **Blocked**: `{blocked}` users\n"
        f"👻 **Deactivated**: `{deactivated}` users"
    )

# --------------------------------------------- Bot Initialization ---------------------------------------------
if __name__ == "__main__":
    print("🤖 Bot is now online!")
    app.run()
