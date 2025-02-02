import json
import logging
import os
import datetime

import pandas as pd

from config import PATH_TO_OPERATIONS
from src.reports import write_to_file_decorator
from src.utils import (
    date_converter,
    greeting,
    file_xlsx_reader,
    dataframe_filter_by_date,
    dataframe_filter_by_operation,
    dataframe_filter_by_source,
    get_card_data,
    get_top_transactions,
    get_exchange_rates,
    get_stock_prices,
)
from logging import DEBUG

logger = logging.getLogger("views")
logger.setLevel(DEBUG)
abs_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../logs", "views.log"))
file_handler = logging.FileHandler(abs_file_path, mode="w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s %(filename)s %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

def main_page(date_and_time: str) -> object:
    """Основная функция для отображения главной страницы. Связывает функциональности из модуля utils, принимает строку
    с датой и временем в формате YYYY-MM-DD HH:MM:SS возвращает JSON-ответ с приветствием, соответствующем времени,
    данными по картам за входящий месяц (4 последние цифры, общая сумма расходов, сумма кэшбека), топ-5 транзакций,
    курс валют и стоимость акций"""
    logger.info("Начало работы")
    result = {}
    try:
        logger.info("Перевод строки в формат DateTime")
        date_obj = date_converter(date_and_time)
        logger.info("Получение приветствия")
        greetings = greeting(date_obj)
        result["greeting"] = greetings
        logger.info(f"Открытие файла {PATH_TO_OPERATIONS}")
        operations_df = file_xlsx_reader(PATH_TO_OPERATIONS)
        logger.info("Фильтрация данных по дате и статусу")
        operations_df_filtered_all = dataframe_filter_by_operation(dataframe_filter_by_date(operations_df, date_obj))
        logger.info("Фильтрация данных по источнику")
        operations_df_filtered_card = dataframe_filter_by_source(operations_df_filtered_all)
        logger.info("Получение данных по картам")
        cards = get_card_data(operations_df_filtered_card)
        result["cards"] = cards
        logger.info("Получение топ-5 транзакций")
        top_transactions = get_top_transactions(operations_df_filtered_all)
        result["top_transactions"] = top_transactions
        logger.info("Получение курса валют")
        currency_rates = get_exchange_rates(date_obj)
        result["currency_rates"] = currency_rates
        logger.info("Получение стоимости акций")
        stock_prices = get_stock_prices(date_obj)
        result["stock_prices"] = stock_prices
        final_result = json.dumps(result, indent=4, ensure_ascii=False)
    except Exception:
        logger.error("Произошла ошибка. Обратитесь к файлу utils.log для подробностей.")
        raise Exception("Произошла ошибка. Обратитесь к файлу utils.log для подробностей.")
    else:
        logger.info("Завершено успешно")
        return final_result
