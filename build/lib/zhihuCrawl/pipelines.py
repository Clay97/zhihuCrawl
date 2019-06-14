# -*- coding: utf-8 -*-
import json
import pymongo
from zhihuCrawl.items import UserInfoItem
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

class ZhihucrawlPipeline(object):
    def __init__(self, mongo_url, mongo_db):
        #self.file = open('userinfo.txt', 'w')
        self.mongo_url = mongo_url
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls,crawler):
        return cls(
            mongo_url = crawler.settings.get('MONGO_URL'),
            mongo_db = crawler.settings.get('MONGO_DATABASE','zhihu')
        )

    def open_spider(self,spider):
        self.client =  pymongo.MongoClient(self.mongo_url)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        #f = json.dumps(dict(item))+'\n'
        #self.file.write(f)
        if isinstance(item, UserInfoItem):
            self._provess_user_item(item)
        else:
            self._process_relation_item(item)
        return item

    def _provess_user_item(self,item):
        self.db.UserInfo.insert(dict(item))

    def _process_relation_item(self,item):
        self.db.Relation.insert(dict(item))
