import json
import time
from typing import Iterable
from urllib.parse import urlencode

import scrapy
from scrapy import Request
from scrapy.http import Response


class AlkotekaDetailSpider(scrapy.Spider):
    name = "alkoteka_spider"
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'FEED_FORMAT': 'json',
        'FEED_URI': 'result.json',
        'DOWNLOAD_DELAY': 0.5,  # Задержка между запросами
        'ROBOTSTXT_OBEY': False,
    }

    # UUID для Краснодара
    CITY_UUID = "4a70f9e0-46ae-11e7-83ff-00155d026416"

    # Ссылки на категории
    START_URLS = [
        # "https://alkoteka.com/catalog/slaboalkogolnye-napitki-2",
        "https://alkoteka.com/catalog/krepkiy-alkogol",
#         "https://alkoteka.com/catalog/bezalkogolnye-napitki-1"
    ]

    def start_requests(self):
        """Загружает список товаров из каждой категории."""
        for category_url in self.START_URLS:
            category_slug = category_url.split("/")[-1]
            api_url = self.build_list_api_url(category_slug, page=1)
            yield scrapy.Request(
                url=api_url,
                callback=self.parse_product_list,
                meta={"category_slug": category_slug, "page": 1},
            )

    def build_list_api_url(self, category_slug: str, page: int = 1, per_page: int = 20):
        """Генерирует URL API списка товаров."""
        base_url = "https://alkoteka.com/web-api/v1/product"
        params = {
            "city_uuid": self.CITY_UUID,
            "page": page,
            "per_page": per_page,
            "root_category_slug": category_slug,
        }
        return f"{base_url}?{urlencode(params)}"

    def parse_product_list(self, response):
        """Извлекает `slug` товаров и парсит каждую карточку."""
        data = json.loads(response.text)
        products = data.get("results", [])

        # Парсим каждый товар
        for product in products:
            slug = product.get("slug")
            product_url = product.get("product_url")
            if slug:
                detail_url = self.build_detail_api_url(slug)
                yield scrapy.Request(
                    url=detail_url,
                    callback=self.parse_product_detail,
                    meta={"product_url": product_url}
                )

        # Пагинация
        if data.get("meta", {}).get("has_more_pages"):
            next_page = response.meta["page"] + 1
            next_api_url = self.build_list_api_url(
                category_slug=response.meta["category_slug"],
                page=next_page,
            )
            yield scrapy.Request(
                url=next_api_url,
                callback=self.parse_product_list,
                meta={"category_slug": response.meta["category_slug"], "page": next_page},
            )

    def build_detail_api_url(self, slug: str):
        """Генерирует URL API карточки товара."""
        return f"https://alkoteka.com/web-api/v1/product/{slug}?city_uuid={self.CITY_UUID}"

    def parse_product_detail(self, response: Response):
        """Парсит полные данные из карточки."""
        product = json.loads(response.text)["results"]
        yield {
            "timestamp": int(time.time()),
            "RPC": product.get("uuid", ""),
            "url": response.meta["product_url"],
            "title": self.build_title(product),
            "marketing_tags": self.get_marketing_tags(product),
            "brand": self.get_brend(product),
            "section": self.get_section(product),
            "price_data": self.get_price_data(product),
            "stock": {
                "in_stock": True if int(product.get("quantity_total")) > 0 else False,
                "count": product.get("quantity_total", 0),
            },
            "assets": {
                "main_image": product.get("image_url", ""),
                "set_images": [""],
                "view360": [""],
                "video": [""],
            },
            "metadata": self.get_metadata(product),
            "variants": 1,
        }



    # Вспомогательные методы
    def build_title(self, product):
        name = product.get("name")
        filter_labels = product.get("filter_labels")
        if filter_labels:
            for filter_label in filter_labels:
                if filter_label.get("title"):
                    name += f", {filter_label['title']}"
        return name

    def get_marketing_tags(self, product):
        marketing_tags = []
        if product.get("new"):
            marketing_tags.append("Новинка")
        if product.get("gift_package"):
            marketing_tags.append("Подарочная упаковка")
        return marketing_tags

    def get_brend(self, product):
        brand_name = ""
        description_blocks = product.get("description_blocks")
        for block in description_blocks:
            if block["code"] == "brend":
                values = block["values"][0]
                brand_name = values.get("name")
        return brand_name

    def get_section(self, product):
        parent_name, category_name = "", ""
        category = product.get("category")
        if category:
            category_name = category.get("name", "")
        parent = category.get("parent")
        if parent:
            parent_name = parent.get("name", "")
        return [parent_name, category_name]

    def get_price_data(self, product):
        original_price = product.get("prev_price")
        current_price = product.get("price")
        has_discount = original_price != current_price
        sale_tag = ""
        if has_discount:
            discount = int((1 - original_price / current_price) * 100)
            sale_tag = f"Скидка {discount}%"
        return {
            "current": float(current_price) if has_discount else float(original_price),
            "original": float(original_price),  # Оригинальная цена.
            "sale_tag": sale_tag
        }

    def get_metadata(self, product):
        meta_dict = {}

        text_blocks = product.get("text_blocks")
        if text_blocks and len(text_blocks) > 0:
            description = text_blocks[0].get("content")
            meta_dict["__description"] = description
        else:
            meta_dict["__description"] = ""

        description = ""
        article = product.get("vendor_code")
        if article:
            meta_dict["article"] = article



        filter_labels = product.get("filter_labels")
        for fl in filter_labels:
            meta_dict[fl["filter"]] = fl["title"]

        return meta_dict
