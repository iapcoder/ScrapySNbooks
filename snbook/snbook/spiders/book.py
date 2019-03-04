# -*- coding: utf-8 -*-
import scrapy
from snbook.items import SnbookItem
from copy import deepcopy
import re


class BookSpider(scrapy.Spider):
    name = 'book'
    allowed_domains = ['suning.com']
    start_urls = ['http://book.suning.com/']

    def parse(self, response):

        item = SnbookItem()
        menu_items = response.xpath("//div[@class='menu-item']")
        menu_subs = response.xpath("//div[contains(@class, 'menu-sub')]")


        for index, menu_item in enumerate(menu_items):
            item["first_cate"] = menu_item.xpath("./dl//h3//text()").extract_first()
            second_items = menu_subs[index].xpath("./div[@class='submenu-left']//p")
            for items in second_items:
                item["second_cate"] = items.xpath(".//a/text()").extract_first()
                # print(item)
                third_items = items.xpath("./following-sibling::ul[1]//li")
                for li in third_items:
                    item["third_cate"] = li.xpath("./a/text()").extract_first()
                    item["third_cate_url"] = li.xpath("./a/@href").extract_first()

                    # print(item["third_cate_url"])
                    if item["third_cate_url"] is not None:

                        # 处理每个分类下的book信息
                        yield scrapy.Request(
                            item["third_cate_url"],
                            callback=self.process_cate_url,
                            meta={"item": deepcopy(item)}
                        )

    # 处理每个分类下的图书
    def process_cate_url(self, response):

        item = response.meta["item"]
        product_lists = response.xpath("//div[@id='filter-results']//li[contains(@class, 'product')]")

        for product in product_lists:
            item["book_img_url"] = "https:"+product.xpath(".//img/@src2").extract_first()
            item["book_name"] = product.xpath(".//img/@alt").extract_first()
            item["book_detail_url"] = "https:"+product.xpath(".//a[@class='sellPoint']/@href").extract_first()
            item["book_comments_num"] = product.xpath(".//p[@class='com-cnt']/a[1]/text()").extract_first()

            item["price_url_param1"] = product.xpath("./@class").extract_first()
            item["price_url_param1"] = re.sub("\s+","-",item["price_url_param1"]).split("-")

            item['cp'] = None
            item['ci'] = None
            item['currentPage'] = None
            item['pageNumbers'] = None




            # 处理每一本图书详情页
            yield scrapy.Request(
                item["book_detail_url"],
                callback=self.process_book_detail,
                meta={"item":deepcopy(item)}
            )


        item['ci'] = response.request.url.split('-')[-2]
        item['currentPage'] = int(re.findall('param.currentPage = "(.*?)";', response.body.decode())[0])
        item['pageNumbers'] = int(re.findall('param.pageNumbers = "(.*?)";',response.body.decode())[0])


        item['cp'] = item['currentPage']
        # 上面的连接只能获得前30本书，一共有60本书，后半段在另一个链接里
        next_part_url = "https://list.suning.com/emall/showProductList.do?ci={}&pg=03&cp={}&il=0&iy=0&adNumber=0&n=1&ch=4&prune=0&sesab=ACBAAB&id=IDENTIFYING&cc=010&paging=1&sub=0".format(item['ci'],item['cp'])

        # print(next_part_url)

        yield scrapy.Request(
            next_part_url,
            callback=self.process_next_product,
            meta={"item":deepcopy(item)}

        )




    def process_next_product(self, response):

        item = response.meta["item"]
        product_lists = response.xpath("//div[@id='filter-results']//li[contains(@class, 'product')]")

        for product in product_lists:
            item["book_img_url"] = "https:" + product.xpath(".//img/@src2").extract_first()
            item["book_name"] = product.xpath(".//img/@alt").extract_first()
            item["book_detail_url"] = "https:" + product.xpath(".//a[@class='sellPoint']/@href").extract_first()
            item["book_comments_num"] = product.xpath(".//p[@class='com-cnt']/a[1]/text()").extract_first()

            item["price_url_param1"] = product.xpath("./@class").extract_first()
            item["price_url_param1"] = re.sub("\s+", "-", item["price_url_param1"]).split("-")

            # 处理每一本图书详情页
            yield scrapy.Request(
                item["book_detail_url"],
                callback=self.process_book_detail,
                meta={"item": deepcopy(item)}
            )

        # # 翻页
        if item['currentPage'] < item['pageNumbers']:

            item['cp'] =item['currentPage'] + 1
            next_page_url = "https://list.suning.com/emall/showProductList.do?ci={}&pg=03&cp={}&il=0&iy=0&adNumber=0&n=1&ch=4&prune=0&sesab=ACBAAB&id=IDENTIFYING&cc=010".format(item['ci'],item['cp'])

            yield scrapy.Request(
                next_page_url,
                callback=self.process_next_product,
                meta={"item": deepcopy(item)}
            )



    def process_book_detail(self, response):

        item = response.meta["item"]

        item["book_author"] = response.xpath("//ul[contains(@class, 'bk-publish')]/li[1]/text()").extract_first()
        item["book_author"] = re.sub("\s","",item["book_author"]) if item["book_author"] else None

        item["book_publisher"] = response.xpath("//ul[contains(@class, 'bk-publish')]/li[2]/text()").extract_first()
        item["book_publisher"] = re.sub("\s","",item["book_publisher"]) if item["book_publisher"] else None

        item["book_publish_date"] = response.xpath("//ul[contains(@class, 'bk-publish')]/li[3]/span[2]/text()").extract_first()

        item["price_url_param2"] = re.findall('"weight":"(.*?)",', response.body.decode())[0]


        # print(item["price_url_param1"][2])
        # print(item["price_url_param2"])

        param1 = item["price_url_param1"][2]
        param2 = item["price_url_param1"][3]
        param3 = item["price_url_param2"]
        item['book_price_url'] = "https://pas.suning.com/nspcsale_0_000000000{}_000000000{}_{}_10_010_0100101_502282_1000000_9017_10106_Z001___R9011205_{}___.html".format(param1,param1,param2,param3)

        # print(price_url)

        # 获取价格
        yield scrapy.Request(
            item['book_price_url'],
            callback=self.get_price,
            meta={"item":deepcopy(item)}
        )


    def get_price(self, response):

        item = response.meta["item"]

        book_price = re.findall('"netPrice":"(.*?)",', response.body.decode())
        item["book_price"] = book_price[0] if book_price else None

        yield item


