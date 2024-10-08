from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from conversation_states import ConversationState

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    username_telegram = update.message.from_user.username
    user_account = context.bot.config.get_user_account(username_telegram)
    
    if user_account:
        if user_account.is_active:
            if user_account.is_login:
                await update.message.reply_text("You are already logged in! Here's the menu...")
                await context.bot.show_menu(update, context)
                return ConversationState.MENU
            else:
                context.user_data['user_account'] = user_account
                await update.message.reply_text(f"Welcome! Please enter your Instagram password for @{user_account.username_instagram}")
                return ConversationState.PASSWORD
        else:
            await update.message.reply_text("Your account is inactive. Please contact support.")
            return ConversationHandler.END
    else:
        await update.message.reply_text("Telegram username not found. Please try again.")
        return ConversationHandler.END

async def password_instagram(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_account = context.user_data['user_account']
    password = update.message.text

    try:
        user_account.uploader.password_instagram = password
        await update.message.reply_text("Enter Email:")
        return ConversationState.EMAIL
    except Exception as e:
        await update.message.reply_text(f"Login error: {str(e)}. Please try again.")
        return ConversationState.PASSWORD

async def email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    email = update.message.text
    user_account = context.user_data['user_account']
    
    try:
        user_account.uploader.password_instagram = email
        await update.message.reply_text("Enter password Email")
        return ConversationState.PASSWORD_EMAIL
    except Exception as e:
        await update.message.reply_text(f"Email verification failed: {str(e)}")
        return ConversationState.EMAIL

async def password_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_account = context.user_data['user_account']
    password_email = update.message.text

    async def login_task():
        user_account.uploader.password_email = password_email
        user_account.uploader.username = user_account.username_instagram
        if user_account.uploader.login_user():
            user_account.is_login = True
            await context.bot.show_menu(update, context)
            return ConversationState.MENU
        else:
            await update.message.reply_text("Login failed. Please try again.")
            return ConversationState.PASSWORD

    try:
        return await context.bot.send_waiting_message(update, context, login_task)
    except Exception as e:
        await update.message.reply_text(f"Login error: {str(e)}. Please try again.")
        return ConversationState.PASSWORD

async def handle_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    code = update.message.text
    await context.bot.instagram_bot.set_code(code)
    await update.message.reply_text("Code received. Attempting to complete login...")
    return ConversationState.MENU