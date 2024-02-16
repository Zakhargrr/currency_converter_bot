import logging
import requests
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

TG_TOKEN = os.getenv('TG_TOKEN')
API_KEY = os.getenv('API_KEY')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "Добро пожаловать в бот-конвертер валюты! \n\nДля получения списка команд введите /help"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "Список команд:\n\n/start - Начало взаимодействия с ботом\n/help - Информация о доступных командах\n/currencies - Список доступных валют\n/convert - Конвертировать валюту"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


async def currencies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = f'https://api.freecurrencyapi.com/v1/currencies?apikey={API_KEY}'
    response = requests.get(url)
    print(response.json())
    text = 'Доступные для конвертирования валюты:\n\n'
    for key, value in response.json()['data'].items():
        name = value["name"]
        string = f"{key} - {name}\n"
        text += string

    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


async def convert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args_list = context.args
    if not args_list:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Неверный формат команды\n\nНапишите команду в виде /convert AMOUNT CUR1 to CUR2\nПример: /convert 100 RUB to USD")
        return

    if len(args_list) != 4:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Неверный формат команды\n\nНапишите команду в виде /convert AMOUNT CUR1 to CUR2\nПример: /convert 100 RUB to USD")
        return

    if args_list[2] not in ['to', 'TO']:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Неверный формат команды\n\nНапишите команду в виде /convert AMOUNT CUR1 to CUR2\nПример: /convert 100 RUB to USD")
        return
    args_list[1], args_list[3] = args_list[1].upper(), args_list[3].upper()
    url = f'https://api.freecurrencyapi.com/v1/latest?apikey={API_KEY}&base_currency={args_list[1]}&currencies={args_list[3]}'
    response = requests.get(url)
    if response.status_code == 422:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Неверное обозначение валюты\n\nДля просмотра списка доступных валют введите команду /currencies")
        return

    amount = int(args_list[0])
    dict_rate = response.json()["data"].values()
    rate = float([x for x in dict_rate][0])
    exchanged_amount = amount * rate
    exchanged_amount_rounded = round(exchanged_amount, 2)
    text = f"{amount} {args_list[1]} равно {exchanged_amount_rounded} {args_list[3]}"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Такой команнды не существует. Введите /help для получения списка команд")


async def message_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Введите команду из списка /help")


if __name__ == '__main__':
    application = ApplicationBuilder().token(TG_TOKEN).build()

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    help_handler = CommandHandler('help', help_menu)
    application.add_handler(help_handler)

    currencies_handler = CommandHandler('currencies', currencies)
    application.add_handler(currencies_handler)

    convert_handler = CommandHandler('convert', convert)
    application.add_handler(convert_handler)

    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    application.add_handler(unknown_handler)

    message_handler = MessageHandler(filters.TEXT, message_response)
    application.add_handler(message_handler)

    application.run_polling()
