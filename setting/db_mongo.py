# -*- coding: utf-8 -*-
import pymongo
from setting import config


class DBMongo:
    def __init__(self):
        # self.mongo_uri = db_setting.MONGO_URI
        # self.mongo_db = db_setting.MONGO_DB
        self.client = pymongo.MongoClient(config.MONGO_URI)
        self.db = self.client[config.MONGO_DB]

    # def open_spider(self):
    #     self.client = pymongo.MongoClient(self.mongo_uri)
    #     self.setting = self.client[self.mongo_db]

    # def close_spider(self):
    #     self.client.close()

    def process_item(self, item):
        self.db[config.MONGO_COLLECTION].insert(dict(item))
        self.client.close()
        # return item

