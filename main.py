
import telebot
from config import TOKEN, currency_dict
from extensions import ConversationException, CurrencyConverter
from math import floor


bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start', 'help'])
def help_message(message: telebot.types.Message):

    text = (
        'Чтобы использовать бота, введите данные в следующем формате:\n\n' +
        '<имя валюты> <в какую валюту перевести>\n\n' +
        'расположение количества валюты не имеет значения, в отличие от названий валют' +
        'для конкретных примеров: /examples\n\n'
        'Список всех доступных валют: /values'
    )

    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['examples'])
def currency_input_examples(message: telebot.types.Message):

    currency_input_example = (
        'Ввод данных поддерживается в таких форматах: \n\n' +
        '<количество валюты> <валюта, из которой хотим перевести> <валюта, в которую хотим перевести>\n\n' +
        '<валюта, из которой хотим перевести> <количество валюты> <валюта, в которую хотим перевести>\n\n' +
        '<валюта, из которой хотим перевести> <валюта, в которую хотим перевести> <количество валюты>\n\n' +
        'Также, все данные необходимо разделять пробелом'
    )

    bot.send_message(message.chat.id, currency_input_example)


@bot.message_handler(commands=['values'])
def currency_information(message: telebot.types.Message):

    message_text = 'Список всех доступных валют:\n'

    for key in currency_dict:
        message_text = '\n'.join((message_text, f'{key} ({currency_dict[key]})'))

    bot.send_message(message.chat.id, message_text)


@bot.message_handler(content_types=['text'])
def convert_currency(message: telebot.types.Message):

    message_parts = message.text.split()

    try:
        convert_from, convert_to, converted_amount = CurrencyConverter.convert_currency(message_parts)

    except ConversationException as error_msg:
        bot.send_message(message.chat.id, f'Ошибка ввода: \n{error_msg}')

    except Exception as error_msg:
        bot.send_message(message.chat.id, f'Ошибка сервера: \n{error_msg}')

    else:

        for index, element in enumerate(message_parts):
            if element.isdigit():
                break

        primal_amount = int(message_parts[index])

        readable_convert_from, readable_convert_to = CurrencyConverter.make_readable(
            convert_from, convert_to,
            primal_amount, converted_amount
        )

        bot_message = (
            f'{primal_amount} {readable_convert_from} ({currency_dict[convert_from]}) = ' +
            f'{floor(converted_amount)} {readable_convert_to} ({currency_dict[convert_to]})'
        )

        bot.send_message(message.chat.id, bot_message)


bot.polling(none_stop=True)
