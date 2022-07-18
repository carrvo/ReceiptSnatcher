"""
Provides a SQLite3 database backend.

https://docs.python.org/3/library/sqlite3.html
https://www.sqlite.org/index.html
https://stackoverflow.com/a/6318154/7163041
"""

import sqlite3

def round_monetary(value):
    """
    Perform a rounding operation to the second decimal point,
    such that it does not include partial cents for the
    monetary systems that support cents.
    """
    return round(value, 2)

class FetchGenerator(object):
    """
    A generator for fetching rows from a database query.
    """

    def __init__(self, cursor):
        """
        Initialize self. See help(type(self)) for accurate signature.
        """
        self.cursor = cursor

    def __iter__(self):
        """
        Iterable.
        """
        return self

    def __next__(self):
        """
        Iterator.
        """
        row = self.cursor.fetchone()
        if row is None:
            self.cursor.close()
            raise StopIteration
        return row

    def __del__(self):
        """
        Cleanup.
        """
        self.cursor.close()

class DatabaseLayer(object):
    """
    Boundary between the application and the database.
    """

    def __init__(self, database, uri=False):
        """
        Initialize self. See help(type(self)) for accurate signature.
        """
        self.connection = sqlite3.connect(database, uri=uri,
                                          detect_types=sqlite3.PARSE_DECLTYPES)
        self.connection.row_factory = sqlite3.Row

    def __enter__(self):
        """
        Creates table schema.
        """
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS Receipt (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            business_name TEXT NOT NULL,
            image BLOB NOT NULL,
            total REAL NOT NULL CHECK(total>0)
        )
        ''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS Item (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL CHECK(price>0),
            quantity REAL CHECK(quantity>0),
            receipt INTEGER NOT NULL,
            FOREIGN KEY(receipt) REFERENCES Receipt(id)
        )
        ''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS Tag(
            path TEXT NOT NULL,
            item INTEGER NOT NULL,
            FOREIGN KEY(item) REFERENCES Item(id),
            PRIMARY KEY(path, item)
        )
        ''')
        cursor.close()
        return self

    def __exit__(self, *exc_details):
        """
        Cleanup.
        """
        self.connection.close()

    def insert(self, business_name, image, total, row_dicts):
        """
        Inserts a new receipt information into the database.

        :business_name: The name of the business the transaction took place with.
        :image: The legal document from which the information was obtained.
        :total: The transaction total.
        :row_dicts: A list of dictionaries, each representing a row.
            :name: The item name.
            :price: The monetary value of the item.
            :quantity: [optional] The amount of the item.
        """
        if total != round_monetary(sum(row.get('price') for row in row_dicts)):
            raise ValueError
        cursor = self.connection.cursor()
        cursor.execute('INSERT INTO Receipt(business_name, image, total) values(?, ?, ?)',
                        (business_name, image, round_monetary(total)))
        receipt_id = cursor.lastrowid
        cursor.executemany('INSERT INTO Item(name, price, quantity, receipt) values(?, ?, ?, ?)',
                           (
                                (row.get('name'), round_monetary(row.get('price')), row.get('quantity'), receipt_id)
                                for row
                                in row_dicts
                           ))
        cursor.close()

    def add_tag(self, item, path):
        """
        Inserts a new tag into the database.

        :item: The item object to tag.
        :path: A path that uniquely identifies the tag
            (use ` / ` to denote sub-tags).
        """
        assert isinstance(item, sqlite3.Row)
        cursor = self.connection.cursor()
        cursor.execute('INSERT INTO Tag(item, path) values(?, ?)',
                       (item['id'], path))
        cursor.close()

    def remove_tag(self, item, path):
        """
        Removes an existing tag from the database.

        :item: The item object to tag.
        :path: A path that uniquely identifies the tag
            (use ` / ` to denote sub-tags).
        """
        assert isinstance(item, sqlite3.Row)
        cursor = self.connection.cursor()
        cursor.execute('DELETE FROM Tag WHERE item == ? AND path == ?',
                       (item['id'], path))
        cursor.close()

    @property
    def receipts(self):
        """
        Retrieves the receipt transaction from the database.
        """
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM Receipt')
        return FetchGenerator(cursor)

    @property
    def items(self):
        """
        Retrieves the receipt items from the database.
        """
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM Item')
        return FetchGenerator(cursor)

    @property
    def tags(self):
        """
        Retrieves the tags from the database.
        """
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM Tag')
        return FetchGenerator(cursor)

class BusinessFilter(object):
    """
    Filters receipts based on their business name.
    """

    def __init__(self, database):
        """
        Initialize self. See help(type(self)) for accurate signature.
        """
        self.database = database

    def __call__(self, name):
        """
        Retrieves receipt transactions from the database.
        """
        cursor = self.database.connection.cursor()
        cursor.execute('SELECT * FROM Receipt WHERE business_name == ?',
                       (name,))
        return FetchGenerator(cursor)

class ItemFilter(object):
    """
    Filters items based on their name.
    """

    def __init__(self, database):
        """
        Initialize self. See help(type(self)) for accurate signature.
        """
        self.database = database

    def __call__(self, name):
        """
        Retrieves receipt items from the database.
        """
        cursor = self.database.connection.cursor()
        cursor.execute('SELECT * FROM Item WHERE name == ?',
                       (name,))
        return FetchGenerator(cursor)

class PriceFilter(object):
    """
    Filters items based on their price.

    :limit: When true will act as an upper boundary;
        when false will act as a lower boundary.
    """

    def __init__(self, database, *, limit=True):
        """
        Initialize self. See help(type(self)) for accurate signature.
        """
        self.database = database
        self.limit = '<' if limit else '>'

    def __call__(self, price):
        """
        Retrieves receipt items from the database.
        """
        cursor = self.database.connection.cursor()
        cursor.execute('SELECT * FROM Item WHERE price {} ?'.format(self.limit),
                       (price,))
        return FetchGenerator(cursor)

class ReceiptFilter(object):
    """
    Filters items based on their receipt.
    """

    def __init__(self, database):
        """
        Initialize self. See help(type(self)) for accurate signature.
        """
        self.database = database

    def __call__(self, receipt):
        """
        Retrieves receipt items from the database.
        """
        assert isinstance(receipt, sqlite3.Row)
        cursor = self.database.connection.cursor()
        cursor.execute('SELECT * FROM Item WHERE receipt == ?',
                       (receipt['id'],))
        return FetchGenerator(cursor)

class TagFilter(object):
    """
    Filters items based on a tag.
    """

    def __init__(self, database):
        """
        Initialize self. See help(type(self)) for accurate signature.
        """
        self.database = database

    def __call__(self, path):
        """
        Retrieves receipt items from the database.
        """
        cursor = self.database.connection.cursor()
        cursor.execute('SELECT * FROM Item WHERE id in (SELECT item FROM Tag WHERE path LIKE ?)',
                       ('{}%'.format(path),))
        return FetchGenerator(cursor)
