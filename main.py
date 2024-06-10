import boto3
import botocore
import os
import logging
from botocore.config import Config
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext, filters

from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

TELEGRAM_API_TOKEN = os.getenv('TELEGRAM_API_TOKEN')

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Hi! I am InstaBobrBot\nI'm here to download Instagram reels to your Telegram channel.")
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

async def handle_message(update: Update, context: CallbackContext) -> None:
    message_text = update.message.text
    if is_valid_url(message_text):
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        await context.application.create_task(download_instagram_reel(message_text, update))
    else:
        # Ignore non-Instagram links
        return
def is_valid_url(url: str) -> bool:
    import re
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:www\.)?instagram\.com/reels/)'  # Instagram reel URL
    )
    return re.match(regex, url) is not None

async def download_instagram_reel(url: str, update: Update) -> None:
    import requests
    await update.message.reply_chat_action(action="typing")
    from instaloader import Instaloader, Post
    try:
        loader = Instaloader()
        post = Post.from_shortcode(loader.context, url.split("/")[-2])
        video_url = post.video_url
        video_response = requests.get(video_url)
        if video_response.status_code == 200:
            region_name = os.getenv('AWS_REGION')
            s3 = boto3.client(
                's3',
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region_name=region_name,
                endpoint_url=os.getenv('S3_ENDPOINT_URL'),
                config=Config(s3={'addressing_style': 'path'})
            )
            bucket_name = os.getenv('S3_BUCKET_NAME')
            import hashlib
            file_name = f"reel_{hashlib.md5(url.encode()).hexdigest()}.mp4"
            # Check if the file already exists in S3
            try:
                s3.head_object(Bucket=bucket_name, Key=file_name)
                video_url = s3.generate_presigned_url('get_object', Params={'Bucket': bucket_name, 'Key': file_name}, ExpiresIn=3600)
                await update.message.reply_video(video=video_url, filename=file_name)
            except botocore.exceptions.ClientError as e:
                if e.response['Error']['Code'] == '404':
                    s3.put_object(Bucket=bucket_name, Key=file_name, Body=video_response.content)
                    await update.message.reply_video(video=video_response.content, filename=file_name)
                else:
                    raise
        else:
            await update.message.reply_text("Failed to download the video.")
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchBucket':
            logger.error(f"Bucket {bucket_name} does not exist. Please check the bucket name and try again.")
            await update.message.reply_text(f"An error occurred: The specified bucket does not exist. Please check the bucket name and try again.")
        else:
            import traceback
            logger.error(f"An error occurred: {str(e)}\n{traceback.format_exc()}")
            await update.message.reply_text(f"An error occurred: {str(e)}\n{traceback.format_exc()}")
            print(traceback.format_exc())
def main():
    if not TELEGRAM_API_TOKEN:
        print("🚨 Oops! The TELEGRAM_API_TOKEN 🔑 environment variable is missing. 🚨")
        print("Let's fix that together! 😊 Here's how:\n" +
              "1. 🌐 Open the Telegram app and search for the BotFather or go to https://t.me/botfather 🌐\n" +
              "2. ✏️ Start a chat with BotFather and send the command /newbot. ✏️\n" +
              "3. 🤖 Follow the instructions to set up your new bot, providing a name and username. 🤖\n" +
              "4. 🔑 Once your bot is created, BotFather will provide you with a TELEGRAM_API_TOKEN. 🔑\n" +
              "5. 📋 Copy this token. 📋\n" +
              "6. 🔐 Set this value in the Env Secrets tab 🔐\n")
        return

    application = Application.builder().token(TELEGRAM_API_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot has successfully connected and started polling. 🚀")
    application.run_polling()

if __name__ == "__main__":
    main()