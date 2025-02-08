import pandas as pd


def file_xlsx_reader_dict(path_to_file: str) -> list[dict]:
    """Функция принимает путь до файла в формате xlsx и возвращает список словарей, с которым в последствии можно
    работать."""
    transaction_data_exel = pd.read_excel(path_to_file, parse_dates=True)
    transaction_data_exel = transaction_data_exel.fillna(0)
    transaction_list = transaction_data_exel.to_dict("records")
    return transaction_list
