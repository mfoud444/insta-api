import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from datetime import datetime, timedelta
import asyncio


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Define conversation states
MAIN_MENU, SELECT_TIME, SELECT_SERVICE, SELECT_UPLOAD_TYPE, SELECT_UPLOAD_METHOD = range(5)

# Define callback data
ADD_TASK, SHOW_TASKS = 'add_task', 'show_tasks'
UPLOAD_STORE, UPLOAD_ACCOUNT = 'upload_store', 'upload_account'
UPLOAD_IMAGE, UPLOAD_VIDEO, UPLOAD_ALBUM = 'upload_image', 'upload_video', 'upload_album'
UPLOAD_URL, UPLOAD_MEDIA = 'upload_url', 'upload_media'

# Store for scheduled tasks
scheduled_tasks = []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [
        [InlineKeyboardButton("Add new task", callback_data=ADD_TASK)],
        [InlineKeyboardButton("Show current tasks", callback_data=SHOW_TASKS)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Welcome to the Scheduler Bot! What would you like to do?', reply_markup=reply_markup)
    return MAIN_MENU

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    if query.data == ADD_TASK:
        await query.edit_message_text("Please enter the time to run the task (format: YYYY-MM-DD HH:MM)")
        return SELECT_TIME
    elif query.data == SHOW_TASKS:
        if not scheduled_tasks:
            await query.edit_message_text("No tasks currently scheduled.")
        else:
            task_list = "\n".join([f"Task: {task['service']} - {task['type']} at {task['time']}" for task in scheduled_tasks])
            await query.edit_message_text(f"Current scheduled tasks:\n{task_list}")
        return ConversationHandler.END

async def select_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    time_str = update.message.text
    try:
        task_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
        context.user_data['task_time'] = task_time
        keyboard = [
            [InlineKeyboardButton("Upload to store", callback_data=UPLOAD_STORE)],
            [InlineKeyboardButton("Upload to account", callback_data=UPLOAD_ACCOUNT)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Select the service:", reply_markup=reply_markup)
        return SELECT_SERVICE
    except ValueError:
        await update.message.reply_text("Invalid time format. Please use YYYY-MM-DD HH:MM")
        return SELECT_TIME

async def select_service(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data['service'] = query.data
    
    if query.data == UPLOAD_STORE:
        keyboard = [
            [InlineKeyboardButton("Upload image", callback_data=UPLOAD_IMAGE)],
            [InlineKeyboardButton("Upload video", callback_data=UPLOAD_VIDEO)]
        ]
    else:  # UPLOAD_ACCOUNT
        keyboard = [
            [InlineKeyboardButton("Upload image", callback_data=UPLOAD_IMAGE)],
            [InlineKeyboardButton("Upload video", callback_data=UPLOAD_VIDEO)],
            [InlineKeyboardButton("Upload album", callback_data=UPLOAD_ALBUM)]
        ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Select upload type:", reply_markup=reply_markup)
    return SELECT_UPLOAD_TYPE

async def select_upload_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data['upload_type'] = query.data
    
    keyboard = [
        [InlineKeyboardButton("Upload from URL", callback_data=UPLOAD_URL)],
        [InlineKeyboardButton("Select from media", callback_data=UPLOAD_MEDIA)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Select upload method:", reply_markup=reply_markup)
    return SELECT_UPLOAD_METHOD

async def select_upload_method(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data['upload_method'] = query.data
    
    task = {
        'time': context.user_data['task_time'],
        'service': context.user_data['service'],
        'type': context.user_data['upload_type'],
        'method': context.user_data['upload_method']
    }
    scheduled_tasks.append(task)
    
    await query.edit_message_text(f"Task scheduled for {task['time']}:\nService: {task['service']}\nType: {task['type']}\nMethod: {task['method']}")
    
    # Schedule the task
    context.job_queue.run_once(execute_task, task['time'], data=task, chat_id=query.message.chat_id)
    
    return ConversationHandler.END

async def execute_task(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    task = job.data
    await context.bot.send_message(job.chat_id, text=f"Executing task:\nService: {task['service']}\nType: {task['type']}\nMethod: {task['method']}")
    # Here you would implement the actual upload logic based on the task details

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Operation cancelled.")
    return ConversationHandler.END

def main() -> None:
    application = Application.builder().token("8052659086:AAEgETCBhOodKd-yVZv6IlC6ZCzmSsWiLbw").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MAIN_MENU: [CallbackQueryHandler(main_menu)],
            SELECT_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_time)],
            SELECT_SERVICE: [CallbackQueryHandler(select_service)],
            SELECT_UPLOAD_TYPE: [CallbackQueryHandler(select_upload_type)],
            SELECT_UPLOAD_METHOD: [CallbackQueryHandler(select_upload_method)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()