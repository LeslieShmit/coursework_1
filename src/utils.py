import datetime
import json
import os
import logging

import pytz

import requests

import pandas as pd
from pandas import DataFrame
from dotenv import load_dotenv
from logging import DEBUG
from config import PATH_TO_USER_SETTINGS, PATH_TO_OPERATIONS

logger = logging.getLogger("utils")
logger.setLevel(DEBUG)
abs_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../logs", "utils.log"))
file_handler = logging.FileHandler(abs_file_path, mode="w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s %(filename)s %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
load_dotenv()

def greeting(date_obj: datetime) -> str:
    """Функция принимает объект datetime и в зависимости от времени возвращает строку с приветствием (Доброе утро:
    6-00 - 11-00, Добрый день: 12-00 - 18-00, Добрый вечер: 18-00 - 00-00, Доброй ночи: 00-00 - 06-00)
    """
    if date_obj.hour < 6:
        logger.info("Время от 00-00 до 06-00: возврат приветствия 'Доброй ночи'")
        result = "Доброй ночи"
    elif 6 <= date_obj.hour < 12:
        logger.info("Время от 06-00 до 12-00: возврат приветствия 'Доброе утро'")
        result = "Доброе утро"
    elif 12 <= date_obj.hour < 18:
        logger.info("Время от 12-00 до 18-00: возврат приветствия 'Добрый день'")
        result = "Добрый день"
    else:
        logger.info("Время от 18-00 до 00-00: возврат приветствия 'Добрый вечер'")
        result = "Добрый вечер"
    return result


def get_card_data(filtered_df: DataFrame) -> list[dict]:
    """Функция принимает отсортированный DataFrame и возвращает список словарей, содержащий последние 4 цифры,
    общую сумму трат и кешбек для каждой карты в DataFrame"""
    logger.info(
        "Считывание отфильтрованных данных с целью вернуть список словарей, содержащий последние 4 цифры, общую сумму трат и кешбек для каждой карты"  # noqa: E501
    )
    card_grouped_df = filtered_df.groupby("Номер карты")
    total_transactions_series = card_grouped_df["Сумма платежа"].sum()
    total_transactions_df = pd.DataFrame(
        {
            "last_digits": total_transactions_series.index,
            "total_spent": total_transactions_series.values,
        }
    )
    total_transactions_df["cashback"] = round(total_transactions_df["total_spent"] / 100, 2)
    card_data = total_transactions_df.to_dict("records")
    for el in card_data:
        el["last_digits"] = el["last_digits"].replace("*", "")
    logger.info("Завершено успешно")
    return card_data


def get_top_transactions(filtered_df: DataFrame) -> list[dict]:
    """Функция принимает отсортированный DataFrame с тратами и возвращает список словарей с 5 самыми большими. В
    словарях помимо суммы траты указаны дата, категория и описание"""
    logger.info("Считывание отфильтрованных данных с целью вернуть список словарей с 5 самыми большими тратами")
    sorted_df = filtered_df.sort_values(by="Сумма платежа")
    sorted_df_top = sorted_df.head()
    sorted_df_top_formatted = sorted_df_top[["Дата операции", "Сумма платежа", "Категория", "Описание"]]
    sorted_df_top_formatted_renamed = sorted_df_top_formatted.rename(
        columns={
            "Дата операции": "date",
            "Сумма платежа": "amount",
            "Категория": "category",
            "Описание": "description",
        }
    )
    sorted_dict_top_formatted_renamed = sorted_df_top_formatted_renamed.to_dict("records")
    for el in sorted_dict_top_formatted_renamed:
        el["date"] = el["date"].to_pydatetime()
        el["date"] = el["date"].strftime("%d.%m.%Y")
    logger.info("Завершено успешно")
    return sorted_dict_top_formatted_renamed


def get_exchange_rates(date_obj: datetime) -> list[dict]:
    """Функция принимает объект datetime и возвращает список словарей, содержащий курсы валют, актуальные на принятую
    дату. Валюты загружаются из файла user_settings.json, находящегося в корне проекта
    """
    logger.info("Запрос на получение курсов валют")
    exchange_rates = []
    date_str = date_obj.strftime("%Y-%m-%d")
    with open(PATH_TO_USER_SETTINGS) as f:
        user_settings = json.load(f)
        user_currencies = user_settings["user_currencies"]
    for currency in user_currencies:
        currency_dict = {"currency": currency}
        api_key = os.getenv("API_KEY_EXCHANGE")
        url = f"https://api.apilayer.com/exchangerates_data/convert?to=RUB&from={currency}&amount=1&date={date_str}"
        payload = {}
        headers = {"apikey": api_key}
        response = requests.request("GET", url, headers=headers, data=payload)
        status_code = response.status_code
        if status_code != 200:
            logger.error(f"Ошибка при запросе курса валюты {currency} {status_code}: {response.reason}")
        response_dict = response.json()
        currency_dict["rate"] = round(float(response_dict["result"]), 2)
        exchange_rates.append(currency_dict)
    logger.info("Завершено успешно")
    return exchange_rates


def get_stock_prices(datetime_obj: datetime) -> list[dict]:
    """Функция принимает объект datetime и возвращает список словарей со стоимостью акций. Компании, стоимость акций
    которых необходимо вернуть, загружаются из файла user_settings.json, находящегося в корне проекта
    """
    logger.info("Запрос на получение стоимости акций")
    stock_prices = []
    eastern_tz = pytz.timezone("US/Eastern")
    datetime_obj = eastern_tz.localize(datetime_obj.replace(tzinfo=None))
    current_date = datetime.datetime.now(tz=pytz.timezone("US/Eastern")).date()
    if datetime_obj.date() == current_date:
        datetime_obj = datetime_obj - datetime.timedelta(days=1)
        datetime_obj = datetime_obj.replace(hour=19, minute=59, second=0)
    else:
        datetime_obj = datetime_obj.replace(second=0)
    if datetime_obj > datetime_obj.replace(hour=19, minute=59, second=0):
        datetime_obj = datetime_obj.replace(hour=19, minute=59, second=0)
    elif datetime_obj < datetime_obj.replace(hour=4, minute=0, second=0):
        datetime_obj = datetime_obj - datetime.timedelta(days=1)
        datetime_obj = datetime_obj.replace(hour=19, minute=59, second=0)
    month_str = datetime_obj.strftime("%Y-%m")
    datetime_obj_original = datetime_obj
    with open(PATH_TO_USER_SETTINGS) as f:
        user_settings = json.load(f)
        user_stocks = user_settings["user_stocks"]
    for stock in user_stocks:
        stock_dict = {"stock": stock}
        api_key = os.getenv("API_KEY_STOCK")
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={stock}&interval=1min&month={month_str}&outputsize=full&apikey={api_key}"  # noqa: E501
        r = requests.get(url)
        status_code = r.status_code
        if status_code != 200:
            logger.error(f"Ошибка при получении стоимости акции {stock} {status_code}: {r.reason}")
        data = r.json()
        datetime_str = datetime_obj.strftime("%Y-%m-%d %H:%M:%S")
        if data == {
            "Information": "Thank you for using Alpha Vantage! Our standard API rate limit is 25 requests per day. Please subscribe to any of the premium plans at https://www.alphavantage.co/premium/ to instantly remove all daily rate limits."  # noqa: E501
        }:
            logger.error("Ошибка. Превышен лимит запросов")
            raise requests.exceptions.RequestException("Превышен лимит запросов")
        while datetime_str not in data["Time Series (1min)"]:
            datetime_obj = datetime_obj - datetime.timedelta(days=1)
            datetime_obj = datetime_obj.replace(hour=19, minute=59, second=0)
            datetime_str = datetime_obj.strftime("%Y-%m-%d %H:%M:%S")
            if datetime_obj < datetime_obj_original.replace(day=1):
                month_str = datetime_obj.strftime("%Y-%m")
                url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={stock}&interval=1min&month={month_str}&outputsize=full&apikey={api_key}"  # noqa: E501
                r = requests.get(url)
                status_code = r.status_code
                if status_code != 200:
                    logger.error(f"Ошибка при получении стоимости акции {stock} {status_code}: {r.reason}")
                data = r.json()
        stock_dict["price"] = round(float(data["Time Series (1min)"][datetime_str]["4. close"]), 2)
        stock_prices.append(stock_dict)
    logger.info("Завершено успешно")
    return stock_prices


def date_converter(date_and_time_str: str) -> datetime:
    """Функция принимает строку с датой и временем в формате YYYY-MM-DD HH:MM:SS и возвращает объект datetime. Если
    дата позже нынешней - выбрасывает ошибку."""
    logger.info("Преобразование даты и времени в объект DateTime")
    date_object = datetime.datetime.strptime(date_and_time_str, "%Y-%m-%d %H:%M:%S")
    if date_object > datetime.datetime.now():
        logger.error("Ошибка. Входящие дата и время не могут быть позже настоящих")
        raise ValueError("Входящие дата и время не могут быть позже настоящих")
    logger.info("Завершено успешно")
    return date_object


def file_xlsx_reader(path_to_file: str) -> DataFrame:
    """Функция принимает путь до файла в формате xlsx и возвращает dataframe, с которым в последствии можно
    работать."""
    logger.info(f"Открытие файла {path_to_file}")
    try:
        transaction_data_exel = pd.read_excel(path_to_file, parse_dates=True)
    except FileNotFoundError:
        logger.error(f"Ошибка: файл {path_to_file} не найден")
        raise FileNotFoundError(f"Ошибка: файл {path_to_file} не найден")
    else:
        transaction_data_exel = transaction_data_exel.fillna(0)
        logger.info("Форматирование данных")
        transaction_list = transaction_data_exel.to_dict("records")
        for transaction_dict in transaction_list:
            date_datetime = datetime.datetime.strptime(transaction_dict["Дата операции"], "%d.%m.%Y %H:%M:%S")
            transaction_dict["Дата операции"] = date_datetime
        df = pd.DataFrame(transaction_list)
        logger.info("Завершено успешно")
        return df


def dataframe_filter_by_date(df: DataFrame, date_obj: datetime) -> DataFrame:
    """Функция отсортировывает входящий DataFrame, оставляя только операции за текущий месяц"""
    logger.info("Начало фильтрации операций по текущему месяцу")
    current_month = date_obj.month
    current_year = date_obj.year
    date_of_start = datetime.datetime(current_year, current_month, 1, 0, 0, 0)
    date_of_start_str = date_of_start.strftime("%Y-%m-%d %H:%M:%S")
    current_date_str = date_obj.strftime("%Y-%m-%d %H:%M:%S")
    filtered_by_date_df = df[(date_of_start_str <= df["Дата операции"]) & (df["Дата операции"] <= current_date_str)]
    logger.info("Завершено успешно")
    return filtered_by_date_df


def dataframe_filter_by_operation(filtered_by_date_df: DataFrame) -> DataFrame:
    """Функция принимает отсортированный по входящей дате DataFrame и возвращает только траты со статусом OK"""
    logger.info("Начало фильтрации операций по статусу")
    filtered_by_operation_df = filtered_by_date_df[
        (filtered_by_date_df["Сумма платежа"] < 0) & (filtered_by_date_df["Статус"] == "OK")
    ]
    logger.info("Завершено успешно")
    return filtered_by_operation_df


def dataframe_filter_by_source(filtered_by_operation_df: DataFrame) -> DataFrame:
    """Функция принимает отсортированный по дате и типу операции DataFrame и возвращает только операции по картам"""
    logger.info("Начало фильтрации операций по источнику")
    filtered_by_source_df = filtered_by_operation_df[filtered_by_operation_df["Номер карты"] != 0]
    logger.info("Завершено успешно")
    return filtered_by_source_df
