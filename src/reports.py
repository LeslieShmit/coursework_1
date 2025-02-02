import json
import os
from typing import Optional, Callable
from dateutil.relativedelta import relativedelta

import pandas as pd
import logging
import datetime
from pandas import DataFrame
from logging import DEBUG

from config import PATH_TO_OPERATIONS, PATH_TO_OUTPUTS
from src.utils import file_xlsx_reader

logger = logging.getLogger("reports")
logger.setLevel(DEBUG)
abs_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../logs", "reports.log"))
file_handler = logging.FileHandler(abs_file_path, mode="w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s %(filename)s %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

def write_to_file_decorator(filename: str) -> Callable:
    """Декоратор принимает имя файла и записывает результат в него. Если файл не существует,
    декоратор его создаст. Файлы хранятся в папке outputs."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            with open(PATH_TO_OUTPUTS / filename, "a", encoding="utf-8") as f:
                logger.info(f"Запись результата в outputs/{filename}")
                f.write(f"Result: {result}\n")
            return result
        return wrapper
    return decorator

@write_to_file_decorator("output_report_by_category.txt")
def report_by_category(transactions: DataFrame, category: str, date: Optional[str] = None) -> object:
    """Функция принимает DataFrame, строку с названием категории и опционально строку с датой в формате
    YYYY-MM-DD HH:MM:SS, а возвращает объект json, содержащий данные об операциях указанной категории за
    последние 3 месяца от указанной даты. Если дата не указана - берется сегодняшняя по умолчанию."""
    logger.info("Начало формирования отчета по категории")
    date_datetime = datetime.datetime.now()
    if date is not None:
        logger.info(f"Указана дата :{date}")
        date_datetime = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    date_to_start_raw = date_datetime - relativedelta(months=3)
    date_to_start = date_to_start_raw.replace(hour=0, minute=0, second=0)
    date_to_start_str = date_to_start.strftime("%Y-%m-%d %H:%M:%S")
    date_datetime_str = date_datetime.strftime("%Y-%m-%d %H:%M:%S")
    filtered_by_date = transactions[(date_to_start_str <= transactions["Дата операции"]) & (transactions["Дата операции"] <= date_datetime_str)]
    filtered_by_category = filtered_by_date[(filtered_by_date["Категория"] == category) & (filtered_by_date["Сумма платежа"] < 0)]
    filtered_by_category_dict = filtered_by_category.to_dict("records")
    if filtered_by_category_dict:
        logger.info("Отчет сформирован")
        for el in filtered_by_category_dict:
            el["Дата операции"] = el["Дата операции"].to_pydatetime()
            el["Дата операции"] = el["Дата операции"].strftime("%d.%m.%Y %H:%M:%S")
        result = json.dumps(filtered_by_category_dict, indent=4, ensure_ascii=False)
    else:
        logger.warning("Внимание! Не найдено ни одной операции. Будет возвращен пустой объект")
        result = json.dumps(filtered_by_category_dict, indent=4, ensure_ascii=False)
    logger.info("Завершено успешно")
    return result
