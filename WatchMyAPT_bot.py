import os
from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from main import run_scraping_job

bot_token = os.getenv('TELEGRAM_BOT_TOKEN')

if bot_token:
    print("Bot token loaded successfully.")
else:
    print("Error: Bot token is not set.")

BOT_USERNAME: Final = '@WatchMyApt_bot'


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hi! I will help you get the best Apartment in Berlin. Send /help for more info.')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('You can enter: Degewo, WBM or Gewobag for the apartments offered by the respective providers')


def handles_response(text: str) -> str:
    text = text.lower()
    if 'degewo' in text:
        return 'Degewo'
    elif 'wbm' in text:
        return 'WBM'
    elif 'gewobag' in text:
        return 'Gewobag'
    else:
        return 'Sorry I don\'t understand.'


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User: ({update.message.chat.id}) in {message_type}\nMessage: {text}')

    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response_key: str = handles_response(new_text)
        else:
            return
    else:
        response_key: str = handles_response(text)

    if response_key == 'Gewobag':
        df = run_scraping_job('Gewobag')

        gewobag_link = "https://www.gewobag.de"
        code_html = f'Here are the offers from {gewobag_link}:'

        if not df.empty:
            # Clean up the addresses because gewobag html sucks
            df['Meta'] = df['Meta'].str.replace(r'^Adresse', '', regex=True)
            df['Meta'] = df['Meta'].str.replace(r'(Berlin).*', r'\1', regex=True)

            for i in range(len(df)):
                code_html += (
                    f'\n\n Address: {df["Meta"].iloc[i]}'
                    f'\n Properties: {df["Properties"].iloc[i]}'
                    f'\n Price: {df["Price-Tag"].iloc[i]}\n'
                )

        response_text = code_html

    elif response_key == 'WBM':
        df = run_scraping_job('WBM')

        WBM_link = "https://www.WBM.de"
        code_html = f'Here are the offers from {WBM_link}:'

        if not df.empty:
             for i in range(len(df)):
                code_html += (
                    f'\n\n Address: {df["Meta"].iloc[i]}'
                    f'\n Properties: {df["Properties"].iloc[i]}'
                    f'\n Price: {df["Price-Tag"].iloc[i]}\n'
                )

        response_text = code_html

    elif response_key == 'Degewo':
        df = run_scraping_job('Degewo')

        degewo_link = "https://www.degewo.de"
        code_html = f'Here are the offers from {degewo_link}:'

        if not df.empty:
            for i in range(len(df)):
                code_html += (
                    f'\n\n Address: {df["Meta"].iloc[i]}'
                    f'\n Properties: {df["Properties"].iloc[i]}'
                    f'\n Price: {df["Price-Tag"].iloc[i]}\n'
                )

        response_text = code_html

    else:
        response_text = response_key

    print('Bot:', response_text)
    await update.message.reply_text(response_text)


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update "{update}" caused error "{context.error}"')


if __name__ == "__main__":

    app = Application.builder().token(bot_token).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_error_handler(error)


    print('Polling started.')
    app.run_polling(poll_interval=3.0)


