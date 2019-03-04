# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
import json
from snbook import settings


class SnbookPipeline(object):

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(host=spider.settings.get('MONGO_HOST'), port=spider.settings.get("MONGO_PORT"))
        self.db = self.client[spider.settings.get("MONGO_DB")]

        file_path = settings.FILE_PATH
        self.f = open(file_path, "a", encoding="utf-8")


    def close_spider(self, spider):
        self.client.close()

        self.f.close()



    def process_item(self, item, spider):

        # 删除item中不需要的字典部分
        del item["price_url_param1"]
        del item["price_url_param2"]
        del item["book_price_url"]
        del item["cp"]
        del item["ci"]
        del item["currentPage"]
        del item["pageNumbers"]


        # 保存到mongodb数据库
        # self.db[spider.settings.get("MONGO_COLLECTION")].insert(dict(item))

        # 保存到本地

        self.f.write(json.dumps(dict(item), ensure_ascii=False, indent=2))
        self.f.write("\n")

        print(item)

        return item


