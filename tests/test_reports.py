import json
from idlelib.iomenu import encoding
from config import PATH_TO_OUTPUTS

import pytest
import pandas as pd
from unittest.mock import mock_open, patch

from src.reports import write_to_file_decorator, report_by_category

def test_write_to_file_decorator():
    mock_file = mock_open()
    with patch("builtins.open", mock_file):
        result = report_by_category(pd.DataFrame([{
        "Дата операции": "03.01.2018 15:03:35",
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
        "Дата операции": "03.01.2018 14:55:21",
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
    }]), "Красота")
        assert result == json.dumps(pd.DataFrame([]).to_dict("records"), indent=4, ensure_ascii=False)
        mock_file.assert_called_once_with(PATH_TO_OUTPUTS / "output_report_by_category.txt", "a", encoding="utf-8")
        mock_file().write.assert_called_once_with("Result: []\n")

def test_report_by_category(df_unfiltered):
    expected_result = [
    {
        "Дата операции": "03.01.2018 14:55:21",
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
        "Сумма операции с округлением": 21.0
    },
    {
        "Дата операции": "01.01.2018 20:27:51",
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
        "Сумма операции с округлением": 316.0
    }
]
    assert report_by_category(pd.DataFrame(df_unfiltered), "Красота", "2018-02-04 09:30:12") == json.dumps(pd.DataFrame(expected_result).to_dict("records"), indent=4, ensure_ascii=False)
