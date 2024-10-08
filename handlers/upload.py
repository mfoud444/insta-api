# handlers/upload_handler.py

import os
from pathlib import Path
from telegram import Update
from telegram.ext import ContextTypes
from conversation_states import ConversationState

async def handle_from_instagram_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    url = update.message.text
    user_account = context.user_data['user_account']
    try:
        media_pk = user_account.uploader.get_media_pk_from_url(url)
        media_info = user_account.uploader.client.media_info(media_pk)
        media_type = media_info.media_type
        upload_type = context.user_data.get('upload_type')

        if media_type == 1:  # Photo
            media_path = user_account.uploader.client.photo_download(media_pk)
            context.user_data['file_path'] = media_path
            context.user_data['upload_type'] = 'Upload Image Story' if upload_type == 'Upload Image Story' else 'Upload Photo'
        elif media_type == 2:  # Video
            media_path = user_account.uploader.client.video_download(media_pk)
            context.user_data['file_path'] = media_path
            context.user_data['upload_type'] = 'Upload Video Story' if upload_type == 'Upload Video Story' else 'Upload Video'
        elif media_type == 8:  # Album
            album_media_paths = [
                user_account.uploader.client.photo_download(item.pk) if item.media_type == 1 else user_account.uploader.client.video_download(item.pk)
                for item in media_info.resources
            ]
            context.user_data['file_path'] = album_media_paths
            context.user_data['upload_type'] = 'Upload Album'
        else:
            await update.message.reply_text("Unsupported media type from the URL.")
            return ConversationState.MENU

        await update.message.reply_text("Media received. Please provide a caption for your post.")
        return ConversationState.WAITING_FOR_CAPTION

    except Exception as e:
        await update.message.reply_text(f"Failed to upload from Instagram URL: {str(e)}")
        return ConversationState.MENU

async def handle_upload_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    upload_choice = update.message.text
    if upload_choice == 'Back':
        await context.bot.show_menu(update, context)
        return ConversationState.MENU
    elif upload_choice == 'Using URL Instagram':
        await update.message.reply_text("Please provide the Instagram post URL to upload.")
        return ConversationState.WAITING_FOR_URL
    elif upload_choice == 'Upload file media':
        await update.message.reply_text("Please send the media file(s) for your upload.")
        return ConversationState.WAITING_FOR_MEDIA

async def handle_caption(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
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

        if isinstance(file_path, str):
            os.remove(file_path)
        elif isinstance(file_path, list):
            for path in file_path:
                os.remove(path)

        await context.bot.show_menu(update, context)
        return ConversationState.MENU

    return await context.bot.send_waiting_message(update, context, caption_task)