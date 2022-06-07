"""
https://docs.python.org/3/library/sqlite3.html
https://www.sqlite.org/index.html
https://stackoverflow.com/a/6318154/7163041
"""

import sqlite3

def round_monetary(value):
    return round(value, 2)

class FetchGenerator(object):
    """
    """

    def __init__(self, cursor):
        self.cursor = cursor

    def __iter__(self):
        return self

    def __next__(self):
        row = self.cursor.fetchone()
        if row is None:
            self.cursor.close()
            raise StopIteration
        return row

    def __del__(self):
        self.cursor.close()

class DatabaseLayer(object):
    """
    """

    def __init__(self, database, uri=False):
        self.connection = sqlite3.connect(database, uri=uri,
                                          detect_types=sqlite3.PARSE_DECLTYPES)
        self.connection.row_factory = sqlite3.Row

    def __enter__(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS Receipt (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image BLOB NOT NULL,
            total REAL NOT NULL CHECK(total>0)
        )
        ''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS Item (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL CHECK(price>0),
            receipt INTEGER NOT NULL,
            FOREIGN KEY(receipt) REFERENCES Receipt(id)
        )
        ''')
        cursor.close()
        return self

    def __exit__(self, *exc_details):
        self.connection.close()

    def insert(self, image, total, row_dicts):
        """
        """
        if total != round_monetary(sum(row.get('price') for row in row_dicts)):
            raise ValueError
        cursor = self.connection.cursor()
        cursor.execute('INSERT INTO Receipt(image, total) values(?, ?)',
                        (image, round_monetary(total)))
        receiptId = cursor.lastrowid
        cursor.executemany('INSERT INTO Item(name, price, receipt) values(?, ?, ?)',
                           (
                                (row.get('name'), round_monetary(row.get('price')), receiptId)
                                for row
                                in row_dicts
                           ))
        cursor.close()

    @property
    def receipts(self):
        """
        """
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM Receipt')
        return FetchGenerator(cursor)

    @property
    def items(self):
        """
        """
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM Item')
        return FetchGenerator(cursor)
