from config import PATH_TO_OPERATIONS
from src.readers import file_xlsx_reader_dict
from src.reports import report_by_category
from src.services import phone_number_search
from src.utils import file_xlsx_reader
from src.views import main_page

if __name__ == "__main__":
    print(main_page("2021-12-12 09:30:12"))
    print(phone_number_search(file_xlsx_reader_dict(PATH_TO_OPERATIONS)))
    print(report_by_category(file_xlsx_reader(PATH_TO_OPERATIONS), "Супермаркеты", "2021-12-12 09:30:12"))
