import datetime

import pandas as pd
from pandas import DataFrame


def greeting(date_obj: datetime) -> str:
    """Функция принимает объект datetime и в зависимости от времени возвращает строку с приветствием (Доброе утро:
     6-00 - 11-00, Добрый день: 12-00 - 18-00, Добрый вечер: 18-00 - 00-00, Доброй ночи: 00-00 - 06-00)"""
    if date_obj.hour < 6:
        result = "Доброй ночи"
    elif 6 <= date_obj.hour < 12:
        result = "Доброе утро"
    elif 12 <= date_obj.hour < 18:
        result = "Добрый день"
    else:
        result = "Добрый вечер"
    return result

def get_card_data(filtered_df: DataFrame) -> list[dict]:
    """Функция принимает отсортированный DataFrame и возвращает список словарей, содержащий последние 4 цифры,
    общую сумму трат и кешбек для каждой карты в DataFrame"""
    card_grouped_df = filtered_df.groupby("Номер карты")
    total_transactions_series = card_grouped_df["Сумма платежа"].sum()
    total_transactions_df = pd.DataFrame({"last_digits": total_transactions_series.index, "total_spent": total_transactions_series.values})
    total_transactions_df["cashback"] = round(total_transactions_df["total_spent"] / 100, 2)
    card_data = total_transactions_df.to_dict("records")
    return card_data



def get_top_transactions():
    pass

def get_exchange_rate():
    pass

def get_stock_prices():
    pass

def date_converter(date_and_time_str: str) -> datetime:
    """Функция принимает строку с датой и временем в формате YYYY-MM-DD HH:MM:SS и возвращает объект datetime"""
    date_object = datetime.datetime.strptime(date_and_time_str, "%Y-%m-%d %H:%M:%S")
    return date_object

def file_xlsx_reader(path_to_file: str) -> DataFrame:
    """Функция принимает путь до файла в формате xlsx и возвращает dataframe, с которым в последствии можно работать."""
    transaction_data_exel = pd.read_excel(path_to_file, parse_dates=True)
    transaction_data_exel = transaction_data_exel.fillna(0)
    transaction_list = transaction_data_exel.to_dict("records")
    for transaction_dict in transaction_list:
        date_datetime = datetime.datetime.strptime(transaction_dict["Дата операции"], "%d.%m.%Y %H:%M:%S")
        transaction_dict["Дата операции"] = date_datetime
    df = pd.DataFrame(transaction_list)
    return df

def dataframe_filter_by_date(df: DataFrame, date_obj: datetime) -> DataFrame:
    """Функция отсортировывает входящий DataFrame, оставляя только операции за текущий месяц"""
    current_month = date_obj.month
    current_year = date_obj.year
    date_of_start = datetime.datetime(current_year, current_month, 1, 0, 0, 0)
    date_of_start_str = date_of_start.strftime("%Y-%m-%d %H:%M:%S")
    current_date_str = date_obj.strftime("%Y-%m-%d %H:%M:%S")
    filtered_by_date_df = df[(date_of_start_str <= df["Дата операции"]) & (df["Дата операции"] <= current_date_str)]
    return filtered_by_date_df

def dataframe_filter_by_operation(filtered_by_date_df: DataFrame) -> DataFrame:
    """Функция принимает отсортированный по входящей дате DataFrame и возвращает только траты со статусом OK и только
    по картам"""
    filtered_df = filtered_by_date_df[(filtered_by_date_df["Сумма платежа"] < 0) & (filtered_by_date_df["Статус"] == "OK") & (filtered_by_date_df["Номер карты"] != 0)]
    return filtered_df

# print(dataframe_filter_by_date(file_xlsx_reader("../data/operations.xlsx"), date_converter("2021-12-22 17:12:22")))
# print(dataframe_filter_by_operation(dataframe_filter_by_date(file_xlsx_reader("../data/operations.xlsx"), date_converter("2019-05-22 17:12:22"))).to_dict("records"))

# print(get_card_data(dataframe_filter_by_operation(dataframe_filter_by_date(file_xlsx_reader("../data/operations.xlsx"), date_converter("2021-12-22 17:12:22")))))