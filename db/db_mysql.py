# -*- coding: utf-8 -*-
import pymysql
from db import db_setting


class DBMysql:
    def __init__(self):
        self.host = db_setting.MYSQL_HOST
        self.database = db_setting.MYSQL_DATABASE
        self.user = db_setting.MYSQL_USER
        self.password = db_setting.MYSQL_PASSWORD
        self.port = db_setting.MYSQL_PORT
        self.table = db_setting.MYSQL_TABLE
        self.db = pymysql.connect(self.host, self.user, self.password, self.database, charset='utf8', port=self.port)
        self.cursor = self.db.cursor()

    # def open_spider(self):
    #     self.db = pymysql.connect(self.host, self.user, self.password, self.database, charset='utf8', port=self.port)
    #     self.cursor = self.db.cursor()

    # def close_spider(self):
    #     self.db.close()

    def process_item(self, item):
        data = dict(item)
        keys = ', '.join(data.keys())
        values = ', '.join(['% s'] * len(data))
        sql = 'insert into % s (% s) values (% s)' % (self.table, keys, values)
        self.cursor.execute(sql, tuple(data.values()))
        self.db.commit()
        return item
