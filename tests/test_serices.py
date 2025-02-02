import pytest
import json

from src.services import phone_number_search


def test_phone_number_search(data_for_phone_search):
    expected_result = [
    {
        "Дата операции": "18.11.2018 14:46:44",
        "Дата платежа": "18.11.2018",
        "Номер карты": 0,
        "Статус": "OK",
        "Сумма операции": -200.0,
        "Валюта операции": "RUB",
        "Сумма платежа": -200.0,
        "Валюта платежа": "RUB",
        "Кэшбэк": 0.0,
        "Категория": "Мобильная связь",
        "MCC": 0.0,
        "Описание": "МТС +7 911 000-09-09",
        "Бонусы (включая кэшбэк)": 2,
        "Округление на инвесткопилку": 0,
        "Сумма операции с округлением": 200.0
    },
    {
        "Дата операции": "17.11.2018 18:53:04",
        "Дата платежа": "19.11.2018",
        "Номер карты": "*7197",
        "Статус": "OK",
        "Сумма операции": -23.8,
        "Валюта операции": "RUB",
        "Сумма платежа": -23.8,
        "Валюта платежа": "RUB",
        "Кэшбэк": 0.0,
        "Категория": "Супермаркеты",
        "MCC": 5411.0,
        "Описание": "Я МТС +7 921 11-22-33",
        "Бонусы (включая кэшбэк)": 0,
        "Округление на инвесткопилку": 0,
        "Сумма операции с округлением": 23.8
    }
]
    assert phone_number_search(data_for_phone_search) == json.dumps(expected_result, indent=4, ensure_ascii=False)

def test_phone_number_search_no_data(data_for_phone_search_not_found):
    expected_result = []
    assert phone_number_search(data_for_phone_search_not_found) == json.dumps(expected_result, indent=4, ensure_ascii=False)
