# Описание
# Парсер интернет-магазина Alkoteka
Scrapy-парсер для сбора данных о товарах с сайта alkoteka.com. Парсер получает полную информацию о товарах, включая цены, наличие, описания и характеристики.

## Содержание

1. [Описание](#Описание)
2. [Функциональность](#функциональность)
3. [Технологии](#технологии)
4. [Установка](#установка)
5. [Использование](#использование)
6. [Контакты](#контакты)

## Функциональность
  - Сбор данных из карточек товаров.
  - Сохранение результатов в JSON-формате.
  - Поддержка региона (Краснодар по умолчанию).

## Технологии
  - **Python 3.10**
  - **Scrapy 2.12.0**

## Установка
1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/SergeyKurilko/alkotekaParser.git
   ```
2. Перейдите в каталог alkotekaParser
   ```bash
   cd alkotekaParser
   ```
3. Создайте виртуальное окружение и активируйте его:
   ```bash
   python3 -m venv venv
   source venv/bin/activate 
   ```
4. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
5. Настройте URL адреса для парсинга:
   - Перейти в каталог `alkotekaParser/alkoteka_parser/spiders`
   - Открыть `alkoteka_spyder.py`
   - В классе AlkotekaDetailSpider найдите атрибут START_URLS и добавьте в список необходимые URL.

## Использование
Запустите парсер командной:
   ```bash
   scrapy crawl alkoteka_spider -O result.json
   ```

## Контакты
email: kurservlad@yandex.ru  
telegram: @Devidbrown
