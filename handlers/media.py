# handlers/media_handler.py

from telegram import Update
from telegram.ext import ContextTypes
from conversation_states import ConversationState

async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.document:
        file = await context.bot.get_file(update.message.document.file_id)
        file_name = update.message.document.file_name
    elif update.message.photo:
        file = await context.bot.get_file(update.message.photo[-1].file_id)
        file_name = f"photo_{update.message.photo[-1].file_id}.jpg"
    elif update.message.video:
        file = await context.bot.get_file(update.message.video.file_id)
        file_name = update.message.video.file_name or f"video_{update.message.video.file_id}.mp4"
    else:
        await update.message.reply_text("Sorry, I couldn't process that media. Please try sending it again.")
        return ConversationState.MENU

    file_path = f"temp_{file_name}"
    await file.download_to_drive(custom_path=file_path)
    context.user_data['file_path'] = file_path
    await update.message.reply_text("Media received. Please provide a caption for your post.")
    return ConversationState.WAITING_FOR_CAPTION