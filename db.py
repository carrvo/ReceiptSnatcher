"""
https://dev.mysql.com/doc/connector-python/en/connector-python-examples.html
"""

from mysql import connector as mysql
from mysql.connector.errors import ProgrammingError,DatabaseError
from flask import request

class DB:
    MySQLUrl = 'my.sql.local'
    SnatcherDB = 'Financial'

    SnatcherTable = 'ReceiptSnatcher'
    
    def __init__(self):
        # kudos to https://stackoverflow.com/a/30060943
        # https://stackoverflow.com/a/24128485
        auth = request.authorization

        self.auth_user = auth.username
        self.auth_pass = auth.password

    def __enter__(self):
        self.connection = mysql.connect(host=DB.MySQLUrl,
                                        user=self.auth_user,
                                        password=self.auth_pass,
                                        database=DB.SnatcherDB,
                                        use_pure=True)
        return self

    def __exit__(self, exc_type, exc, exc_tb):
        self.connection.close()
    
    def insert_ml(self, rows):
        with self.connection.cursor() as cursor:
            row_ids = []
            for row in rows:
                cursor.execute('INSERT INTO ReceiptSnatcher_ML(business_name, parsedItem, correctedItem, parsedPrice, correctedPrice) VALUES(%(business_name)s, %(parsedItem)s, %(correctedItem)s, %(parsedPrice)s, %(correctedPrice)s)', row)
                row_ids.append(cursor.lastrowid)
            return row_ids

    def insert(self, rows):
        with self.connection.cursor() as cursor:
            row_ids = []
            for row in rows:
                cursor.execute('INSERT INTO ReceiptSnatcher(business_name, transaction_date, item, price, quantity) VALUES(%(business_name)s, %(transaction_date)s, %(correctedItem)s, %(correctedPrice)s, %(quantity)s)', row)
                row_ids.append(cursor.lastrowid)
            self.connection.commit()
            return row_ids

    def select(self):
        with self.connection.cursor() as cursor:
            cursor.execute('select * from receiptsnatcher')
            for row in cursor:
                yield row

