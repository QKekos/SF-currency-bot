
import requests
import json
from typing import Union
from fuzzywuzzy import fuzz
from config import currency_dict


class ConversationException(Exception):
    pass


class CurrencyConverter:

    readable_words = {

        'Рубль': {
            0: 'Рублей',
            1: 'Рубль'
        },

        'Доллар': {
            0: 'Долларов',
            1: 'Доллар'
        },

        'Евро': {
            i: 'Евро' for i in range(10)
        },

        'Penny': {
            0: 'копеек',
            1: 'копейка'
        },

        'Cent': {
            0: 'центов',
            1: 'цент'
        }
    }

    for i in range(2, 5):

        readable_words['Доллар'].update({i: 'Доллара'})
        readable_words['Рубль'].update({i: 'Рубля'})

        readable_words['Penny'].update({i: 'копейки'})
        readable_words['Cent'].update({i: 'цента'})

    for i in range(5, 10):

        readable_words['Доллар'].update({i: 'Долларов'})
        readable_words['Рубль'].update({i: 'Рублей'})

        readable_words['Penny'].update({i: 'копеек'})
        readable_words['Cent'].update({i: 'центов'})


    @staticmethod
    def convert_currency(message_parts: list[str, ...]) -> tuple[Union[str, float]]:

        # Base len check

        if len(message_parts) < 3:
            raise ConversationException('Слишком мало аргументов')

        elif len(message_parts) > 3:
            raise ConversationException('Слишком много аргументов')

        # Standardization amount permutations

        if message_parts[0].isdigit():
            message_parts = [message_parts[1], message_parts[2], message_parts[0]]

        elif message_parts[1].isdigit():
            message_parts = [message_parts[0], message_parts[2], message_parts[1]]

        # Primal values

        convert_from = message_parts[0]
        convert_to = message_parts[1]

        if message_parts[2].isdigit() and int(message_parts[2]) > 0:
            amount = int(message_parts[2])

        else:
            raise ConversationException('Введено некорректное количество валюты')

        # Fuzzy comparison

        for key in currency_dict:
            if fuzz.token_sort_ratio(convert_from, key) >= 75:
                convert_from = key

            if fuzz.token_sort_ratio(convert_to, key) >= 75:
                convert_to = key

        # Is currency available

        if convert_from == convert_to:
            raise ConversationException('Перевод валюты саму в себя не требуется')

        elif convert_from not in currency_dict:
            raise ConversationException(f'Валюта {convert_from} не поддерживается')

        elif convert_to not in currency_dict:
            raise ConversationException(f'Валюта {convert_to} не поддерживается')

        # Return data

        api_answer = json.loads(
            requests.get(f'https://api.exchangeratesapi.io/latest?base={currency_dict[convert_from]}').content
        )

        converted_amount = round(api_answer['rates'][currency_dict[convert_to]] * amount, 2)

        return convert_from, convert_to, converted_amount

    @staticmethod
    def make_readable(convert_from: str, convert_to: str, primal_amount: int, converted_amount: int) -> tuple[str, ...]:

        primal_convert_to = 'Penny' if currency_dict[convert_to] == 'RUB' else 'Cent'

        convert_from = CurrencyConverter.readable_words[convert_from][primal_amount % 10]
        convert_to = CurrencyConverter.readable_words[convert_to][int(converted_amount) % 10]

        while int(converted_amount) != converted_amount:
            converted_amount *= 10

        convert_to += (
            f' {int(converted_amount % 100)}' +
            f' {CurrencyConverter.readable_words[primal_convert_to][int(converted_amount) % 10]}'
        )

        return convert_from, convert_to
