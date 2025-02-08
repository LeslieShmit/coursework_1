import json
import logging
import os
import re
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
    pattern = re.compile(r"\+7\s\d+\s\d+.\d+.\d+")
    for el in transactions:
        if re.search(pattern, el["Описание"]) is not None:
            result.append(el)
    if not result:
        logger.warning("Не найдено ни одной операции. Будет возвращен пустой объект")
    final_result = json.dumps(result, indent=4, ensure_ascii=False)
    logger.info("Завершено успешно")
    return final_result
