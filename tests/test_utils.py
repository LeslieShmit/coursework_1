import pytest
import datetime
import pandas as pd

from unittest.mock import patch, mock_open
from freezegun import freeze_time

import requests

from config import PATH_TO_OPERATIONS
from src.utils import (
    greeting,
    date_converter,
    file_xlsx_reader,
    dataframe_filter_by_date,
    dataframe_filter_by_operation,
    dataframe_filter_by_source,
    get_card_data,
    get_top_transactions,
    get_exchange_rates,
    get_stock_prices,
)


@pytest.mark.parametrize(
    "date_obj, expected",
    [
        (datetime.datetime(2025, 1, 1, 9, 30, 12), "Доброе утро"),
        (datetime.datetime(2025, 1, 1, 13, 30, 12), "Добрый день"),
        (datetime.datetime(2025, 1, 1, 19, 30, 12), "Добрый вечер"),
        (datetime.datetime(2025, 1, 1, 1, 30, 12), "Доброй ночи"),
    ],
)
def test_greeting(date_obj, expected):
    assert greeting(date_obj) == expected


@pytest.mark.parametrize(
    "date_str, expected",
    [
        ("2025-01-01 09:30:12", datetime.datetime(2025, 1, 1, 9, 30, 12)),
        ("2025-01-01 13:30:12", datetime.datetime(2025, 1, 1, 13, 30, 12)),
        ("2025-01-01 19:30:12", datetime.datetime(2025, 1, 1, 19, 30, 12)),
        ("2025-01-01 01:30:12", datetime.datetime(2025, 1, 1, 1, 30, 12)),
    ],
)
def test_date_converter(date_str, expected):
    assert date_converter(date_str) == expected


def test_date_converter_error():
    with pytest.raises(ValueError) as exc_info:
        date_converter("2025-05-05 01:01:22")
    assert str(exc_info.value) == "Входящие дата и время не могут быть позже настоящих"


@patch("pandas.read_excel")
def test_file_xlsx_reader(mock_read):
    mock_read.return_value = pd.DataFrame(
        {
            "Дата операции": ["03.01.2018 15:03:35", "03.01.2018 14:55:21"],
            "Дата платежа": ["04.01.2018", "05.01.2018"],
            "Номер карты": ["*7197", "*7197"],
            "Статус": ["OK", "OK"],
            "Сумма операции": [-73.06, -21.0],
            "Валюта операции": ["RUB", "RUB"],
            "Сумма платежа": [-73.06, -21.0],
            "Валюта платежа": ["RUB", "RUB"],
            "Кэшбэк": [0.0, 0.0],
            "Категория": ["Супермаркеты", "Красота"],
            "MCC": [5499.0, 5977.0],
            "Описание": ["Magazin 25", "OOO Balid"],
            "Бонусы (включая кэшбэк)": [1, 0],
            "Округление на инвесткопилку": [0, 0],
            "Сумма операции с округлением": [73.06, 21.0],
        }
    )
    expected_result = pd.DataFrame(
        [
            {
                "Дата операции": datetime.datetime.strptime("03.01.2018 15:03:35", "%d.%m.%Y %H:%M:%S"),
                "Дата платежа": "04.01.2018",
                "Номер карты": "*7197",
                "Статус": "OK",
                "Сумма операции": -73.06,
                "Валюта операции": "RUB",
                "Сумма платежа": -73.06,
                "Валюта платежа": "RUB",
                "Кэшбэк": 0.0,
                "Категория": "Супермаркеты",
                "MCC": 5499.0,
                "Описание": "Magazin 25",
                "Бонусы (включая кэшбэк)": 1,
                "Округление на инвесткопилку": 0,
                "Сумма операции с округлением": 73.06,
            },
            {
                "Дата операции": datetime.datetime.strptime("03.01.2018 14:55:21", "%d.%m.%Y %H:%M:%S"),
                "Дата платежа": "05.01.2018",
                "Номер карты": "*7197",
                "Статус": "OK",
                "Сумма операции": -21.0,
                "Валюта операции": "RUB",
                "Сумма платежа": -21.0,
                "Валюта платежа": "RUB",
                "Кэшбэк": 0.0,
                "Категория": "Красота",
                "MCC": 5977.0,
                "Описание": "OOO Balid",
                "Бонусы (включая кэшбэк)": 0,
                "Округление на инвесткопилку": 0,
                "Сумма операции с округлением": 21.0,
            },
        ]
    )
    assert file_xlsx_reader("test.xlsx").to_dict("records") == expected_result.to_dict("records")


def test_file_xlsx_reader_error():
    with pytest.raises(FileNotFoundError) as exc_info:
        file_xlsx_reader("test.xlsx")
    assert str(exc_info.value) == "Ошибка: файл test.xlsx не найден"


def test_dataframe_filter_by_date(df_unfiltered):
    expected_result = pd.DataFrame(
        [
            {
                "Дата операции": datetime.datetime.strptime("03.01.2018 15:03:35", "%d.%m.%Y %H:%M:%S"),
                "Дата платежа": "04.01.2018",
                "Номер карты": "*7197",
                "Статус": "OK",
                "Сумма операции": -73.06,
                "Валюта операции": "RUB",
                "Сумма платежа": -73.06,
                "Валюта платежа": "RUB",
                "Кэшбэк": 0.0,
                "Категория": "Супермаркеты",
                "MCC": 5499.0,
                "Описание": "Magazin 25",
                "Бонусы (включая кэшбэк)": 1,
                "Округление на инвесткопилку": 0,
                "Сумма операции с округлением": 73.06,
            },
            {
                "Дата операции": datetime.datetime.strptime("03.01.2018 14:55:21", "%d.%m.%Y %H:%M:%S"),
                "Дата платежа": "05.01.2018",
                "Номер карты": "*7197",
                "Статус": "FAILED",
                "Сумма операции": -21.0,
                "Валюта операции": "RUB",
                "Сумма платежа": -21.0,
                "Валюта платежа": "RUB",
                "Кэшбэк": 0.0,
                "Категория": "Красота",
                "MCC": 5977.0,
                "Описание": "OOO Balid",
                "Бонусы (включая кэшбэк)": 0,
                "Округление на инвесткопилку": 0,
                "Сумма операции с округлением": 21.0,
            },
            {
                "Дата операции": datetime.datetime.strptime("01.01.2018 20:27:51", "%d.%m.%Y %H:%M:%S"),
                "Дата платежа": "04.01.2018",
                "Номер карты": "*7197",
                "Статус": "OK",
                "Сумма операции": -316.0,
                "Валюта операции": "RUB",
                "Сумма платежа": -316.0,
                "Валюта платежа": "RUB",
                "Кэшбэк": 0.0,
                "Категория": "Красота",
                "MCC": 5977.0,
                "Описание": "OOO Balid",
                "Бонусы (включая кэшбэк)": 6,
                "Округление на инвесткопилку": 0,
                "Сумма операции с округлением": 316.0,
            },
            {
                "Дата операции": datetime.datetime.strptime("01.01.2018 12:49:53", "%d.%m.%Y %H:%M:%S"),
                "Дата платежа": "01.01.2018",
                "Номер карты": 0,
                "Статус": "OK",
                "Сумма операции": 3000.0,
                "Валюта операции": "RUB",
                "Сумма платежа": 3000.0,
                "Валюта платежа": "RUB",
                "Кэшбэк": 0.0,
                "Категория": "Переводы",
                "MCC": 0.0,
                "Описание": "Линзомат ТЦ Юность",
                "Бонусы (включая кэшбэк)": 0,
                "Округление на инвесткопилку": 0,
                "Сумма операции с округлением": 3000.0,
            },
        ]
    )
    assert dataframe_filter_by_date(pd.DataFrame(df_unfiltered), datetime.datetime(2018, 1, 6, 13, 12, 5)).to_dict(
        "records"
    ) == expected_result.to_dict("records")


def test_dataframe_filter_by_operation(df_filtered_by_date):
    expected_result = pd.DataFrame(
        [
            {
                "Дата операции": datetime.datetime.strptime("03.01.2018 15:03:35", "%d.%m.%Y %H:%M:%S"),
                "Дата платежа": "04.01.2018",
                "Номер карты": "*7197",
                "Статус": "OK",
                "Сумма операции": -73.06,
                "Валюта операции": "RUB",
                "Сумма платежа": -73.06,
                "Валюта платежа": "RUB",
                "Кэшбэк": 0.0,
                "Категория": "Супермаркеты",
                "MCC": 5499.0,
                "Описание": "Magazin 25",
                "Бонусы (включая кэшбэк)": 1,
                "Округление на инвесткопилку": 0,
                "Сумма операции с округлением": 73.06,
            },
            {
                "Дата операции": datetime.datetime.strptime("01.01.2018 20:27:51", "%d.%m.%Y %H:%M:%S"),
                "Дата платежа": "04.01.2018",
                "Номер карты": "*7197",
                "Статус": "OK",
                "Сумма операции": -316.0,
                "Валюта операции": "RUB",
                "Сумма платежа": -316.0,
                "Валюта платежа": "RUB",
                "Кэшбэк": 0.0,
                "Категория": "Красота",
                "MCC": 5977.0,
                "Описание": "OOO Balid",
                "Бонусы (включая кэшбэк)": 6,
                "Округление на инвесткопилку": 0,
                "Сумма операции с округлением": 316.0,
            },
        ]
    )
    assert dataframe_filter_by_operation(pd.DataFrame(df_filtered_by_date)).to_dict(
        "records"
    ) == expected_result.to_dict("records")


def test_dataframe_filter_by_source(df_filtered_by_date_and_operation):
    expected_result = pd.DataFrame(
        [
            {
                "Дата операции": datetime.datetime.strptime("03.01.2018 15:03:35", "%d.%m.%Y %H:%M:%S"),
                "Дата платежа": "04.01.2018",
                "Номер карты": "*7197",
                "Статус": "OK",
                "Сумма операции": -73.06,
                "Валюта операции": "RUB",
                "Сумма платежа": -73.06,
                "Валюта платежа": "RUB",
                "Кэшбэк": 0.0,
                "Категория": "Супермаркеты",
                "MCC": 5499.0,
                "Описание": "Magazin 25",
                "Бонусы (включая кэшбэк)": 1,
                "Округление на инвесткопилку": 0,
                "Сумма операции с округлением": 73.06,
            },
            {
                "Дата операции": datetime.datetime.strptime("03.01.2018 14:55:21", "%d.%m.%Y %H:%M:%S"),
                "Дата платежа": "05.01.2018",
                "Номер карты": "*7198",
                "Статус": "OK",
                "Сумма операции": -21.0,
                "Валюта операции": "RUB",
                "Сумма платежа": -21.0,
                "Валюта платежа": "RUB",
                "Кэшбэк": 0.0,
                "Категория": "Красота",
                "MCC": 5977.0,
                "Описание": "OOO Balid",
                "Бонусы (включая кэшбэк)": 0,
                "Округление на инвесткопилку": 0,
                "Сумма операции с округлением": 21.0,
            },
            {
                "Дата операции": datetime.datetime.strptime("01.01.2018 20:27:51", "%d.%m.%Y %H:%M:%S"),
                "Дата платежа": "04.01.2018",
                "Номер карты": "*7199",
                "Статус": "OK",
                "Сумма операции": -316.0,
                "Валюта операции": "RUB",
                "Сумма платежа": -316.0,
                "Валюта платежа": "RUB",
                "Кэшбэк": 0.0,
                "Категория": "Красота",
                "MCC": 5977.0,
                "Описание": "OOO Balid",
                "Бонусы (включая кэшбэк)": 6,
                "Округление на инвесткопилку": 0,
                "Сумма операции с округлением": 316.0,
            },
        ]
    )
    assert dataframe_filter_by_source(pd.DataFrame(df_filtered_by_date_and_operation)).to_dict(
        "records"
    ) == expected_result.to_dict("records")


def test_get_card_data(df_cards_only):
    expected_result = [
        {"last_digits": "7197", "total_spent": -73.06, "cashback": -0.73},
        {"last_digits": "7198", "total_spent": -21.0, "cashback": -0.21},
        {"last_digits": "7199", "total_spent": -316.0, "cashback": -3.16},
    ]
    assert get_card_data(pd.DataFrame(df_cards_only)) == expected_result


def test_get_top_transactions(df_filtered_by_date_and_operation):
    expected_result = [
        {"date": "01.01.2018", "amount": -4500.0, "category": "Переводы", "description": "Линзомат ТЦ Юность"},
        {"date": "01.01.2018", "amount": -4000.0, "category": "Переводы", "description": "Линзомат ТЦ Юность"},
        {"date": "01.01.2018", "amount": -3000.0, "category": "Переводы", "description": "Линзомат ТЦ Юность"},
        {"date": "01.01.2018", "amount": -316.0, "category": "Красота", "description": "OOO Balid"},
        {"date": "03.01.2018", "amount": -73.06, "category": "Супермаркеты", "description": "Magazin 25"},
    ]
    assert get_top_transactions(pd.DataFrame(df_filtered_by_date_and_operation)) == expected_result


@patch("requests.request")
def test_get_exchange_rates(mock_request):
    mock_request.return_value.json.return_value = {
        "date": "2018-02-22",
        "historical": "",
        "info": {"rate": 148.972231, "timestamp": 1519328414},
        "query": {"amount": 1, "from": "USD", "to": "RUB"},
        "result": 100.12,
        "success": True,
    }
    mocked_open = mock_open(read_data='{"user_currencies": ["USD"], "user_stocks": ["AAPL"]}')
    with patch("builtins.open", mocked_open):
        result = get_exchange_rates(datetime.datetime(2018, 2, 22, 12, 0, 0))
        assert result == [{"currency": "USD", "rate": 100.12}]

@patch("requests.request")
def test_get_stock_prices_current_time(mock_request):
    mock_request.return_value.json.return_value = {
        "Meta Data": {
            "1. Information": "Intraday (1min) open, high, low, close prices and volume",
            "2. Symbol": "IBM",
            "3. Last Refreshed": "2025-01-31 19:59:00",
            "4. Interval": "1min",
            "5. Output Size": "Full size",
            "6. Time Zone": "US/Eastern",
        },
        "Time Series (1min)": {
            "2025-01-31 19:59:00": {
                "1. open": "255.2000",
                "2. high": "255.2000",
                "3. low": "255.1000",
                "4. close": "255.1000",
                "5. volume": "112",
            },
            "2025-01-31 19:58:00": {
                "1. open": "255.4430",
                "2. high": "255.4430",
                "3. low": "255.0250",
                "4. close": "255.3000",
                "5. volume": "175",
            },
            "2025-01-31 19:55:00": {
                "1. open": "254.0370",
                "2. high": "254.0370",
                "3. low": "254.0370",
                "4. close": "254.0370",
                "5. volume": "10",
            },
        },
    }
    mocked_open = mock_open(read_data='{"user_currencies": ["USD"], "user_stocks": ["IBM"]}')
    with freeze_time("2025-02-01 22:00:00"):
        with patch("builtins.open", mocked_open):
            result = get_stock_prices(datetime.datetime(2025, 2, 1, 21, 30, 00))
            assert result == [{"stock": "IBM", "price": 255.10}]
