import re

import json
import logging
import os

from logging import DEBUG


logger = logging.getLogger("services")
logger.setLevel(DEBUG)
abs_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../logs", "services.log"))
file_handler = logging.FileHandler(abs_file_path, mode="w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s %(filename)s %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

def phone_number_search(transactions: list[dict]) -> object:
    """Функция принимает список словарей и возвращает json объект с операциями, в описании которых есть номер
        телефона."""
    logger.info("Начало фильтрации по наличию в описании номера телефона")
    result = []
    pattern = re.compile(r'\+7\s\d+\s\d+.\d+.\d+')
    for el in transactions:
       if re.search(pattern, el["Описание"]) is not None:
           result.append(el)
    if not result:
        logger.warning("Не найдено ни одной операции. Будет возвращен пустой объект")
    final_result = json.dumps(result, indent=4, ensure_ascii=False)
    logger.info("Завершено успешно")
    return final_result

data = [{
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
    "Сумма операции с округлением": 200.0,
}, {
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
    "Сумма операции с округлением": 23.8,
}, {
    "Дата операции": "17.11.2018 17:01:03",
    "Дата платежа": "19.11.2018",
    "Номер карты": "*7197",
    "Статус": "OK",
    "Сумма операции": -57.0,
    "Валюта операции": "RUB",
    "Сумма платежа": -57.0,
    "Валюта платежа": "RUB",
    "Кэшбэк": 0.0,
    "Категория": "Супермаркеты",
    "MCC": 5499.0,
    "Описание": "Колхоз",
    "Бонусы (включая кэшбэк)": 1,
    "Округление на инвесткопилку": 0,
    "Сумма операции с округлением": 57.0,
}]

print(phone_number_search(data))