import os
from telegram import Update, ReplyKeyboardMarkup
import telegram
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes
import logging
from pathlib import Path
from typing import List, Dict
import httpx
from t import t
from config import Config
logger = logging.getLogger()
import asyncio 


write bot python-telegram-bot telegram provide section service scheduler process
when select has show 2 option (add new task , show curren process task )
when select show curren process task  replay message curren process task
if select add new task
ask user what time run task
when enter time ask user what is service show 2 option (upload to store, upload to account)

if upload to store and this has 2 choies (upload image, upload video)
or upload to account this has 3 choies (upload image, upload video , upload album)

the upload process has 3 choies (upload from url , select from media )

and bot run that automatic  do that in time user selected

 
# States
USERNAME, PASSWORD, MENU, WAITING_FOR_URL, WAITING_FOR_USERNAME, WAITING_FOR_HASHTAG, WAITING_FOR_MEDIA, WAITING_FOR_CAPTION, WAITING_FOR_UPLOAD_TYPE, WAITING_FOR_URL_DOWNLOAD , WAITING_FOR_LANGUAGE, CODE, EMAIL , PASSWORD_EMAIL= range(14)



class TelegramBot:
    def __init__(self):
        self.config = Config()
        self.default_language = 'en'


    def get_translation(self, key, lang, **kwargs):
        translation = t.get(lang, t[self.default_language]).get(key, key)
        return translation.format(**kwargs)

    async def set_language(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        keyboard = [['English', 'العربية']]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        await update.message.reply_text(self.get_translation('choose_action', self.default_language), reply_markup=reply_markup)
        return WAITING_FOR_LANGUAGE

    async def language_selected(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        lang = 'en' if update.message.text == 'English' else 'ar'
        self.default_language = lang
        await update.message.reply_text(self.get_translation('welcome', lang))
        return ConversationHandler.END
    
    async def send_waiting_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE, task, *args, **kwargs):
        waiting_message = await update.message.reply_text("Please wait...")
        try:
            result = await task(*args, **kwargs)
            await waiting_message.delete()
            return result
        except telegram.error.TimedOut:
            await waiting_message.delete()
            await update.message.reply_text("The request timed out. Please try again later.")
            return None
        except Exception as e:
            await waiting_message.delete()
            await update.message.reply_text(f"An error occurred: {str(e)}")
            return None


    async def show_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
              ['Upload Image Story', 'Upload Video Story'],
    [ 'Upload Photo' , 'Upload Video' 
   
     ],
        [ 
      'Upload Album', 'Upload IGTV'
     ],
    ['Get User Info', 'Get Hashtag Info'],
    ['Download from Instagram'],
     [ 'Logout']
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        await update.message.reply_text("Choose an action:", reply_markup=reply_markup)

    async def menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        choice = update.message.text
        user_account = context.user_data['user_account']
        if choice in ['Upload Image Story', 'Upload Video Story', 'Upload Photo', 'Upload Video', 'Upload Album', 'Upload IGTV', 'Upload Clip']:
            context.user_data['upload_type'] = choice
            
            keyboard = [['Using URL Instagram', 'Upload file media'], ['Back']]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
            await update.message.reply_text(f"Choose how to upload {choice}:", reply_markup=reply_markup)
            return WAITING_FOR_UPLOAD_TYPE
        elif choice == 'Download from Instagram':
            await update.message.reply_text("Please provide the Instagram post URL to download.")
            return WAITING_FOR_URL_DOWNLOAD
        elif choice == 'Get User Info':
            await update.message.reply_text("Please provide the username to get info.")
            return WAITING_FOR_USERNAME
        elif choice == 'Get Hashtag Info':
            await update.message.reply_text("Please provide the hashtag to get info.")
            return WAITING_FOR_HASHTAG
        elif choice == 'Logout':
            user_account.uploader.client.logout()
            await update.message.reply_text("Logged out. Enter your username to login again.")
            return USERNAME
        return MENU
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        username_telegram = update.message.from_user.username

        user_account = self.config.get_user_account(username_telegram)
        if user_account:
            if user_account.is_active:
                if user_account.is_login:
                    await update.message.reply_text("You are already logged in! Here's the menu...")
                    await self.show_menu(update, context)
                    return MENU
                else:
                    context.user_data['user_account'] = user_account
                    await update.message.reply_text(f"Welcome! Please enter your Instagram password for @{user_account.username_instagram}")
                    return MENU
            else:
                await update.message.reply_text("Your account is inactive. Please contact support.")
                return ConversationHandler.END
        else:
            await update.message.reply_text("Telegram username not found. Please try again.")
            return ConversationHandler.END

    async def password_instagram(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user_account = context.user_data['user_account']
        password = update.message.text
        async def login_task():
            user_account.uploader.password_instagram = password
            user_account.uploader.password_email = ""
            user_account.uploader.username = user_account.username_instagram
            if user_account.uploader.login_user():
                user_account.is_login = True
                await self.show_menu(update, context)
                return MENU
            else:
                await update.message.reply_text("Login failed. Please try again.")
                return PASSWORD
        try:
            return await self.send_waiting_message(update, context, login_task)
        except Exception as e:
            await update.message.reply_text(f"Login error: {str(e)}. Please try again.")
            return PASSWORD
        # try:
        #     user_account.uploader.password_instagram = password
        #     await update.message.reply_text("Enter Email:")
        #     return EMAIL
        # except Exception as e:
        #     await update.message.reply_text(f"Login error: {str(e)}. Please try again.")
        #     return PASSWORD


    async def email(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        email = update.message.text
        user_account = context.user_data['user_account']
        
        try:
            user_account.uploader.password_instagram = email
            await update.message.reply_text("Enter password Email")
            # # Set email in the uploader for further verification
            # user_account.uploader.set_email(email)
            # await update.message.reply_text("Email verified. Please provide the code sent to your email.")
            return PASSWORD_EMAIL
        except Exception as e:
            await update.message.reply_text(f"Email verification failed: {str(e)}")
            return EMAIL


    async def password_email(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user_account = context.user_data['user_account']
        password_email = update.message.text


        async def login_task():
            user_account.uploader.password_email = password_email
            user_account.uploader.username = user_account.username_instagram
            if user_account.uploader.login_user():
                user_account.is_login = True
                await self.show_menu(update, context)
                return MENU
            else:
                await update.message.reply_text("Login failed. Please try again.")
                return PASSWORD
        try:
            return await self.send_waiting_message(update, context, login_task)
        except Exception as e:
            await update.message.reply_text(f"Login error: {str(e)}. Please try again.")
            return PASSWORD
            

        
    async def handle_code(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        code = update.message.text
        await self.instagram_bot.set_code(code)
        await update.message.reply_text("Code received. Attempting to complete login...")
        return MENU


    async def handle_upload_type(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        upload_choice = update.message.text
        if upload_choice == 'Back':
            await self.show_menu(update, context)  
            return MENU
        elif upload_choice == 'Using URL Instagram':
            await update.message.reply_text("Please provide the Instagram post URL to upload.")
            return WAITING_FOR_URL
        elif upload_choice == 'Upload file media':
            await update.message.reply_text("Please send the media file(s) for your upload.")
            return WAITING_FOR_MEDIA


  # Make sure to install this package if you haven't already

    async def handle_download_url(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        url = update.message.text
        user_account = context.user_data['user_account']

        sessionid = "47462899944%3As0vQt3QI4Op0WR%3A16%3AAYdqCTdHTZ4RBEvbzOWIiTNukG6mDQd33mMYQcKGGA"  # Assuming you have the session ID stored in user_account

        async def get_media_pk():
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://furious-trina-sarr-3ce5a089.koyeb.app/media/pk_from_url",
                    params={"url": url}
                )
            if response.status_code == 200:
                try:
                    media_pk = response.text.strip().strip('"')  # Remove any surrounding quotes
                    print(media_pk)
                    return media_pk  
                except ValueError:
                    await update.message.reply_text("Error: Response is not in the expected format.")
                    return None
            else:
                await update.message.reply_text(f"Error retrieving media PK: {response.text}")
                return None

        async def download_task(media_pk):
            try:
                media_pk_int = int(media_pk)  # Convert the cleaned media_pk to an integer
            except ValueError:
                await update.message.reply_text("Invalid media PK format.")
                return

            data = {
                "sessionid": sessionid,
                "media_pk": media_pk_int,
                "returnFile": True,
                # Optionally include "folder": "desired_folder_path" if needed
            }

            async with httpx.AsyncClient() as client:
                response = await client.post("https://furious-trina-sarr-3ce5a089.koyeb.app/video/download", data=data)

            if response.status_code == 200:
       
                    await update.message.reply_video(video=response.content, caption="Video downloaded successfully!")
            else:
                await update.message.reply_text(f"Error downloading video: {response.text}")

        # Use send_waiting_message to handle loading state
        async def handle_download():
            media_pk = await get_media_pk()
            if media_pk:
                await download_task(media_pk)

        # Use the reusable 'send_waiting_message' function
        return await self.send_waiting_message(update, context, handle_download)

    async def handle_from_instagram_url(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        url = update.message.text
        user_account = context.user_data['user_account']
        try:
            media_pk = user_account.uploader.get_media_pk_from_url(url)
            media_info = user_account.uploader.client.media_info(media_pk)
            media_type = media_info.media_type
            upload_type = context.user_data.get('upload_type')
            if media_type == 1:  
                media_path = user_account.uploader.client.photo_download(media_pk)
                context.user_data['file_path'] = media_path

                if upload_type == 'Upload Image Story':
                    context.user_data['upload_type'] = 'Upload Image Story'
                else:
                    context.user_data['upload_type'] = 'Upload Photo'

            elif media_type == 2: 
                media_path = user_account.uploader.client.video_download(media_pk)
                context.user_data['file_path'] = media_path

                if upload_type == 'Upload Video Story':
                    context.user_data['upload_type'] = 'Upload Video Story'
                else:
                    context.user_data['upload_type'] = 'Upload Video'

            elif media_type == 8:  
                album_media_paths = [
                    user_account.uploader.client.photo_download(item.pk) if item.media_type == 1 else user_account.uploader.client.video_download(item.pk)
                    for item in media_info.resources
                ]
                context.user_data['file_path'] = album_media_paths  
                context.user_data['upload_type'] = 'Upload Album'

            else:
                await update.message.reply_text("Unsupported media type from the URL.")
                return MENU
            await update.message.reply_text("Media received. Please provide a caption for your post.")
            return WAITING_FOR_CAPTION

        except Exception as e:
            await update.message.reply_text(f"Failed to upload from Instagram URL: {str(e)}")
            return MENU

    


    async def handle_media(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
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
            return MENU

        file_path = f"temp_{file_name}"
        await file.download_to_drive(custom_path=file_path) 
        context.user_data['file_path'] = file_path
        await update.message.reply_text("Media received. Please provide a caption for your post.")
        return WAITING_FOR_CAPTION



    async def handle_caption(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        caption = update.message.text
        file_path = context.user_data['file_path']
        upload_type = context.user_data['upload_type']
        user_account = context.user_data['user_account']

        async def caption_task():
            try:
                uploader = user_account.uploader
                if upload_type == 'Upload Photo':
                    uploader.photo_upload(Path(file_path), caption)
                elif upload_type == 'Upload Video':
                    uploader.video_upload(Path(file_path), caption)
                elif upload_type == 'Upload Album':
                    uploader.album_upload([Path(file_path)], caption)
                elif upload_type == 'Upload IGTV':
                    uploader.igtv_upload(Path(file_path), "IGTV Title", caption)
                elif upload_type == 'Upload Clip':
                    uploader.clip_upload(Path(file_path), caption)
                elif upload_type == 'Upload Image Story': 
                    uploader.photo_upload_to_story(Path(file_path), caption)
                elif upload_type == 'Upload Video Story':  
                    uploader.upload_video_to_story(Path(file_path), caption)

                await update.message.reply_text(f"{upload_type} successful!")

            except Exception as e:
                await update.message.reply_text(f"Failed to {upload_type}: {str(e)}")

            os.remove(file_path)
            await self.show_menu(update, context)
            return MENU

        return await self.send_waiting_message(update, context, caption_task)

    async def get_user_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
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
            await self.show_menu(update, context)
            return MENU

        return await self.send_waiting_message(update, context, user_info_task)

    async def get_hashtag_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
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
            await self.show_menu(update, context)
            return MENU

        return await self.send_waiting_message(update, context, hashtag_info_task)

    def login_all_accounts(self):
        for account in self.config.get_all_active_accounts():
            session_file = f"{account.username_instagram}.json"
            if os.path.exists(session_file):
                password = 'your_password'  # You should implement a secure way to store and retrieve passwords
                try:
                    # user_account.uploader.username = user_account.username_instagram
                    if account.uploader.login_user():
                        account.is_login = True
                        logger.info(f"Logged in successfully: {account.username_instagram}")
                    else:
                        logger.warning(f"Login failed for {account.username_instagram}")
                except Exception as e:
                    logger.error(f"Error logging in {account.username_instagram}: {str(e)}")

    def run(self):
        application = Application.builder().token(self.config._config.get("bot_token")).build()

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.start)],
            states={
                # USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.username)],
                PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.password_instagram)],
                 CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_code)],
                MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.menu)],
                WAITING_FOR_URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_from_instagram_url)],
                  EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.email)], 
 PASSWORD_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.password_email)],
                WAITING_FOR_URL_DOWNLOAD: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_download_url)],
                WAITING_FOR_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_user_info)],
                WAITING_FOR_HASHTAG: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_hashtag_info)],
                WAITING_FOR_MEDIA: [MessageHandler(filters.Document.ALL | filters.PHOTO | filters.VIDEO, self.handle_media)],
                WAITING_FOR_CAPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_caption)],
                WAITING_FOR_UPLOAD_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_upload_type)],
            },
            fallbacks=[],
        )

        application.add_handler(conv_handler)
        application.run_polling()
