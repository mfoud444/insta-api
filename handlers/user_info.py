# handlers/user_info_handler.py

from telegram import Update
from telegram.ext import ContextTypes
from conversation_states import ConversationState

async def get_user_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    username = update.message.text
    user_account = context.user_data['user_account']

    async def user_info_task():
        try:
            user_info = user_account.uploader.get_user_info(username)
            info_text = f"User Info for {username}:\n"
            info_text += f"Full Name: {user_info.full_name}\n"
            info_text += f"Followers: {user_info.follower_count}\n"
            info_text += f"Following: {user_info.following_count}\n"
            await update.message.reply_text(info_text)
        except Exception as e:
            await update.message.reply_text(f"Failed to get user info: {str(e)}")
        await context.bot.show_menu(update, context)
        return ConversationState.MENU

    return await context.bot.send_waiting_message(update, context, user_info_task)