# handlers/hashtag_info_handler.py

from telegram import Update
from telegram.ext import ContextTypes
from conversation_states import ConversationState

async def get_hashtag_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    hashtag = update.message.text.lstrip('#')
    user_account = context.user_data['user_account']

    async def hashtag_info_task():
        try:
            hashtag_info = user_account.uploader.get_hashtag_info(hashtag)
            info_text = f"Hashtag Info for #{hashtag}:\n"
            info_text += f"Media Count: {hashtag_info.media_count}\n"
            await update.message.reply_text(info_text)
        except Exception as e:
            await update.message.reply_text(f"Failed to get hashtag info: {str(e)}")
        await context.bot.show_menu(update, context)
        return ConversationState.MENU

    return await context.bot.send_waiting_message(update, context, hashtag_info_task)