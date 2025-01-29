import pandas as pd

def greeting():
    pass

def get_card_data():
    pass

def get_top_transactions():
    pass

def get_exchange_rate():
    pass

def get_stock_prices():
    pass

def date_converter():
    pass

def file_xlsx_reader(path_to_file: str) -> list[dict]:
    """Функция принимает путь до файла в формате xlsx и возвращает словарь, с которым в последствии можно работать."""
    transaction_data_exel = pd.read_excel(path_to_file)
    transaction_data_exel = transaction_data_exel.fillna(0)
    transaction_list = transaction_data_exel.to_dict("records")
    return transaction_list
