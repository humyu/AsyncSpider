# -*- coding: utf-8 -*-
import pymysql
from setting import config


class DBMysql:
    def __init__(self):
        self.host = config.MYSQL_HOST
        self.database = config.MYSQL_DATABASE
        self.user = config.MYSQL_USER
        self.password = config.MYSQL_PASSWORD
        self.port = config.MYSQL_PORT
        self.table = config.MYSQL_TABLE
        self.db = pymysql.connect(self.host, self.user, self.password, self.database, charset='utf8', port=self.port)
        self.cursor = self.db.cursor()

    # def open_spider(self):
    #     self.setting = pymysql.connect(self.host, self.user, self.password, self.database, charset='utf8', port=self.port)
    #     self.cursor = self.setting.cursor()

    # def close_spider(self):
    #     self.setting.close()

    def process_item(self, item):
        data = dict(item)
        keys = ', '.join(data.keys())
        values = ', '.join(['% s'] * len(data))
        sql = 'insert into % s (% s) values (% s)' % (self.table, keys, values)
        self.cursor.execute(sql, tuple(data.values()))
        self.db.commit()
        self.db.close()
        # return item
