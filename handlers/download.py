# handlers/download_handler.py

from telegram import Update
from telegram.ext import ContextTypes
from conversation_states import ConversationState

async def handle_download_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    url = update.message.text
    user_account = context.user_data['user_account']

    async def download_task():
        try:
            media_pk = user_account.uploader.get_media_pk_from_url(url)
            media_info = user_account.uploader.client.media_info(media_pk)
            media_type = media_info.media_type

            if media_type == 1:  # Photo
                media_path = user_account.uploader.client.photo_download(media_pk)
                await update.message.reply_photo(photo=open(media_path, 'rb'), caption="Photo downloaded successfully!")
            elif media_type == 2:  # Video
                media_path = user_account.uploader.client.video_download(media_pk)
                await update.message.reply_video(video=open(media_path, 'rb'), caption="Video downloaded successfully!")
            elif media_type == 8:  # Album
                album_media_paths = [
                    user_account.uploader.client.photo_download(item.pk) if item.media_type == 1 else user_account.uploader.client.video_download(item.pk)
                    for item in media_info.resources
                ]
                for media_path in album_media_paths:
                    if media_info.media_type == 1:
                        await update.message.reply_photo(photo=open(media_path, 'rb'))
                    else:
                        await update.message.reply_video(video=open(media_path, 'rb'))
                await update.message.reply_text("Album downloaded successfully!")
            elif media_type == 17:  # IGTV
                media_path = user_account.uploader.client.video_download(media_pk)
                await update.message.reply_video(video=open(media_path, 'rb'), caption="IGTV downloaded successfully!")
            else:
                await update.message.reply_text("Unsupported media type from the URL.")
                return ConversationState.MENU
        except Exception as e:
            await update.message.reply_text(f"Failed to download: {str(e)}")

        await context.bot.show_menu(update, context)
        return ConversationState.MENU

    return await context.bot.send_waiting_message(update, context, download_task)