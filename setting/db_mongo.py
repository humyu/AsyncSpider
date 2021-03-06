# -*- coding: utf-8 -*-
import pymongo
from setting import db_setting


class DBMongo:
    def __init__(self):
        # self.mongo_uri = db_setting.MONGO_URI
        # self.mongo_db = db_setting.MONGO_DB
        self.client = pymongo.MongoClient(db_setting.MONGO_URI)
        self.db = self.client[db_setting.MONGO_DB]

    # def open_spider(self):
    #     self.client = pymongo.MongoClient(self.mongo_uri)
    #     self.setting = self.client[self.mongo_db]

    # def close_spider(self):
    #     self.client.close()

    def process_item(self, item):
        self.db[db_setting.MONGO_COLLECTION].insert(dict(item))
        return item


