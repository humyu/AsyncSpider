# -*- coding: utf-8 -*-
import pymongo
from db import db_setting


class DBMongo(object):
    def __init__(self):
        # self.mongo_uri = db_setting.MONGO_URI
        # self.mongo_db = db_setting.MONGO_DB
        self.client = pymongo.MongoClient(db_setting.MONGO_URI)
        self.db = self.client[db_setting.MONGO_DB]

    # def open_spider(self):
    #     self.client = pymongo.MongoClient(self.mongo_uri)
    #     self.db = self.client[self.mongo_db]

    def process_item(self, item):
        self.db[db_setting.MONGO_COLLECTION].insert(dict(item))
        return item

    # def close_spider(self):
    #     self.client.close()
