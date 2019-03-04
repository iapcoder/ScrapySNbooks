# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SnbookItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    first_cate = scrapy.Field()
    second_cate = scrapy.Field()
    third_cate = scrapy.Field()

    third_cate_url = scrapy.Field()
    # third_cate_url_2 = scrapy.Field()

    book_img_url = scrapy.Field()
    book_name = scrapy.Field()
    book_detail_url = scrapy.Field()
    book_price = scrapy.Field()
    book_comments_num = scrapy.Field()
    book_author = scrapy.Field()
    book_publisher = scrapy.Field()
    book_publish_date = scrapy.Field()

    ci = scrapy.Field()
    cp = scrapy.Field()
    currentPage = scrapy.Field()
    pageNumbers = scrapy.Field()

    price_url_param1 = scrapy.Field()
    price_url_param2 = scrapy.Field()
    book_price_url = scrapy.Field()
