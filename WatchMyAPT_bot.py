import os
from typing import Final

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from config import housing_association
from main import run_scraping_job

bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
BOT_USERNAME: Final = '@WatchMyApt_bot'

live_ticker_set = False
old_dfs = None


def check_valid_bot_token():
    if bot_token:
        print("Bot token loaded successfully.")
    else:
        print("Error: Bot token is not set.")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hi! I will help you get the best Apartment in Berlin. Send /help for more info.')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'You can view all currently available apartments from specific providers by entering one of the following options: \"Degewo\", \"WBM\", or \"Gewobag\".\n\nTo receive instant notifications when a new apartment becomes available, activate the live ticker by typing \"start live ticker\". To stop these notifications, just type \"end live ticker\".'
    )


def handles_response(text: str) -> str:
    responses = {
        'degewo': 'Degewo',
        'wbm': 'WBM',
        'gewobag': 'Gewobag',
        'start live ticker': 'live',
        'end live ticker': 'end ticker'
    }

    text = text.lower()

    for key, response in responses.items():
        if key in text:
            return response

    return "Sorry I don't understand. Please try /help for more info."


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global live_ticker_set

    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User: ({update.message.chat.id}) in {message_type}\nMessage: {text}')

    # Handle group messages that mention the bot
    if message_type == 'group' and BOT_USERNAME in text:
        text = text.replace(BOT_USERNAME, '').strip()

    response_key: str = handles_response(text)

    if response_key in ['Gewobag', 'WBM', 'Degewo']:
        response_text = await generate_apartment_offers(response_key)
    elif response_key == 'live':
        response_text = await start_live_ticker(update, context)
    elif response_key == 'end ticker':
        response_text = await stop_live_ticker(context)
    else:
        response_text = response_key

    print('Bot:', response_text)
    await update.message.reply_text(response_text)


async def generate_apartment_offers(provider: str) -> str:
    df = run_scraping_job(provider)
    link_dict = {
        'Gewobag': "https://www.gewobag.de",
        'WBM': "https://www.WBM.de",
        'Degewo': "https://www.degewo.de"
    }

    offers = f'Here are the offers from {link_dict[provider]}:'

    if not df.empty:
        # Clean the addresses and format the offers
        df['Meta'] = df['Meta'].str.replace(r'^Adresse', '', regex=True)
        df['Meta'] = df['Meta'].str.replace(r'(Berlin).*', r'\1', regex=True)

        for i in range(len(df)):
            offers += (
                f'\n\n Address: {df["Meta"].iloc[i]}'
                f'\n Properties: {df["Properties"].iloc[i]}'
                f'\n Price: {df["Price-Tag"].iloc[i]}\n'
            )

    return offers


async def start_live_ticker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    global live_ticker_set

    if live_ticker_set is False:
        context.job_queue.run_repeating(
            live_ticker,
            interval=150,
            first=0,
            chat_id=update.effective_message.chat_id,
            name='live_ticker')
        live_ticker_set = True
        return "I've started the live ticker! :)"
    else:
        return "Live ticker already running."


async def stop_live_ticker(context: ContextTypes.DEFAULT_TYPE) -> str:
    global live_ticker_set

    if live_ticker_set is True:
        live_ticker_set = False
        current_jobs = context.job_queue.get_jobs_by_name('live_ticker')

        for job in current_jobs:
            job.schedule_removal()

        return "I've stopped the live ticker. You will no longer receive notifications."
    else:
        return "Live ticker is not running."


async def live_ticker(context: ContextTypes.DEFAULT_TYPE):
    global old_dfs
    print("live ticker started")

    if old_dfs is None:
        old_dfs = []
        for association in housing_association:
            old_dfs.append((association, run_scraping_job(association)))

    new_dfs = []
    for association in housing_association:
        new_dfs.append((association, run_scraping_job(association)))

    results = []
    for i in range(len(new_dfs)):
        assoc_name, new_df = new_dfs[i]
        _, old_df = old_dfs[i]  # Only need the DataFrame from old_dfs
        diff_df = new_df[~new_df.apply(tuple, 1).isin(old_df.apply(tuple, 1))]
        if not diff_df.empty:
            results.append((assoc_name, diff_df))

    code_html = 'A new Apartment was found:'
    for assoc_name, result in results:
        if len(result.values) > 0:
            code_html += (
                f'\n\n Provider: {assoc_name}'
                f'\n Address: {result["Meta"].values[0]}'
                f'\n Properties: {result["Properties"].values[0]} m²'
                f'\n Price: {result["Price-Tag"].values[0]} Euro\n'
            )

    response_text = code_html

    if response_text != 'A new Apartment was found:':
        await context.bot.send_message(context.job.chat_id, response_text)

    old_dfs = new_dfs


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update "{update}" caused error "{context.error}"')


if __name__ == "__main__":
    check_valid_bot_token()
    print('Starting bot...')
    app = Application.builder().token(bot_token).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_error_handler(error)

    print('Polling started.')
    app.run_polling(poll_interval=3.0, allowed_updates=Update.ALL_TYPES)
