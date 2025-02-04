# Coursework_1
## Описание:
Приложение предназначено для анализа транзакций, находящихся в excel-файле.
Оно возвращает 3 отдельных JSON-ответа:
- JSON-ответ, возвращающий приветствие, соответствующее времени суток, список словарей, содержащий последние 4 цифры, общую сумму трат и кешбек для каждой карты на входящий месяц, 5 самых больших транзакций с датой и категорией, курс валют и акций, актуальные на входящую дату.
- JSON-ответ, возвращающий операции, в описании которых есть номер телефона.
- JSON-ответ, возвращающий операции в заданной категории за 3 месяца, предшествующие заданной дате.

Список валют и акций хранится в корне проекта в файле user_settings.json
Excel-файл хранится в папке data

## Установка:
1. Клонируйте репозиторий
```
git clone https://github.com/LeslieShmit/homework_1.git
```
2. Установите poetry в качестве пакетного менеджера
```
poetry init
```
3. Установите необходимые зависимости
```
poetry install
```
## Тестирование:
Для тестирования проекта используется зависимость pytest.
Для тестирования запустите следующий код:
```
pytest
```

Для отображения процента покрытия запустите следующий код:
```
pytest --cov
```
