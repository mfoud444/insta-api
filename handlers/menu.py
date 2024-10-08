# handlers/menu_handler.py
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from conversation_states import ConversationState

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    choice = update.message.text
    user_account = context.user_data['user_account']
    
    if choice in ['Upload Image Story', 'Upload Video Story', 'Upload Photo', 'Upload Video', 'Upload Album', 'Upload IGTV', 'Upload Clip']:
        context.user_data['upload_type'] = choice
        keyboard = [['Using URL Instagram', 'Upload file media'], ['Back']]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        await update.message.reply_text(f"Choose how to upload {choice}:", reply_markup=reply_markup)
        return ConversationState.WAITING_FOR_UPLOAD_TYPE
    elif choice == 'Download from Instagram':
        await update.message.reply_text("Please provide the Instagram post URL to download.")
        return ConversationState.WAITING_FOR_URL_DOWNLOAD
    elif choice == 'Get User Info':
        await update.message.reply_text("Please provide the username to get info.")
        return ConversationState.WAITING_FOR_USERNAME
    elif choice == 'Get Hashtag Info':
        await update.message.reply_text("Please provide the hashtag to get info.")
        return ConversationState.WAITING_FOR_HASHTAG
    elif choice == 'Logout':
        user_account.uploader.client.logout()
        await update.message.reply_text("Logged out. Enter your username to login again.")
        return ConversationState.USERNAME
    return ConversationState.MENU

# handlers/language_handler.py
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from conversation_states import ConversationState

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [['English', 'العربية']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text(context.bot.get_translation('choose_action', context.bot.default_language), reply_markup=reply_markup)
    return ConversationState.WAITING_FOR_LANGUAGE

async def language_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = 'en' if update.message.text == 'English' else 'ar'
    context.bot.default_language = lang
    await update.message.reply_text(context.bot.get_translation('welcome', lang))
    return ConversationHandler.END