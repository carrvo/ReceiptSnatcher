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

    def __init__(self, cursor, *primary_keys):
        """
        Initialize self. See help(type(self)) for accurate signature.
        """
        self.cursor = cursor
        self.primary_keys = lambda row: {key:row[key] for key in primary_keys}

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

    def __eq__(self, value):
        """
        Return self==value.
        """
        return tuple(
            self.primary_keys(row)
            for row
            in tuple(self)
        ) == tuple(
            self.primary_keys(row)
            for row
            in tuple(value)
        )

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
            date DATE NOT NULL,
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

    def insert(self, business_name, image, date, total, row_dicts):
        """
        Inserts a new receipt information into the database.

        :business_name: The name of the business the transaction took place with.
        :image: The legal document from which the information was obtained.
        :date: The transaction date.
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
        cursor.executemany('INSERT INTO Item(name, date, price, quantity, receipt) values(?, ?, ?, ?, ?)',
                           (
                                (row.get('name'), date, round_monetary(row.get('price')), row.get('quantity'), receipt_id)
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
        return FetchGenerator(cursor, 'id')

    @property
    def items(self):
        """
        Retrieves the receipt items from the database.
        """
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM Item')
        return FetchGenerator(cursor, 'id')

    def _filter_items(self, *, criteria, values, **kargs):
        """
        Retrieves receipt items from the database.
        """
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM Item WHERE {}'
                       ''.format(' AND '.join(criteria)),
                       values)
        return FetchGenerator(cursor, 'id')

    @property
    def tags(self):
        """
        Retrieves the tags from the database.
        """
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM Tag')
        return FetchGenerator(cursor, 'path', 'item')

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
        return FetchGenerator(cursor, 'id')

class ItemFilter(object):
    """
    Filters items based on their name.
    """

    def __init__(self, database):
        """
        Initialize self. See help(type(self)) for accurate signature.
        """
        self.database = database

    def _filter_items(self, *, name, criteria=tuple(), values=tuple(), **kwargs):
        """
        Retrieves receipt items from the database.
        """
        criteria = list(criteria)
        values = list(values)
        criteria.append('name == ?')
        values.append(name)
        return self.database._filter_items(criteria=criteria, values=values, **kwargs)

    def __call__(self, *, name, **kwargs):
        """
        Retrieves receipt items from the database.
        """
        return self._filter_items(name=name, **kwargs)

class PriceFilter(object):
    """
    Filters items based on their price.
    """

    def __init__(self, database):
        """
        Initialize self. See help(type(self)) for accurate signature.
        """
        self.database = database

    def _filter_items(self, *, lower_price_boundary=None, upper_price_boundary=None, criteria=tuple(), values=tuple(), **kwargs):
        """
        Retrieves receipt items from the database.
        """
        criteria = list(criteria)
        values = list(values)
        if lower_price_boundary is not None:
            criteria.append('price > ?')
            values.append(lower_price_boundary)
        if upper_price_boundary is not None:
            criteria.append('price < ?')
            values.append(upper_price_boundary)
        return self.database._filter_items(criteria=criteria, values=values, **kwargs)

    def __call__(self, *, lower_price_boundary=None, upper_price_boundary=None, **kwargs):
        """
        Retrieves receipt items from the database.
        """
        return self._filter_items(lower_price_boundary=lower_price_boundary, upper_price_boundary=upper_price_boundary, **kwargs)

class ReceiptFilter(object):
    """
    Filters items based on their receipt.
    """

    def __init__(self, database):
        """
        Initialize self. See help(type(self)) for accurate signature.
        """
        self.database = database

    def _filter_items(self, *, receipt, criteria=tuple(), values=tuple(), **kwargs):
        """
        Retrieves receipt items from the database.
        """
        criteria = list(criteria)
        values = list(values)
        assert isinstance(receipt, sqlite3.Row)
        criteria.append('receipt == ?')
        values.append(receipt['id'])
        return self.database._filter_items(criteria=criteria, values=values, **kwargs)

    def __call__(self, *, receipt, **kwargs):
        """
        Retrieves receipt items from the database.
        """
        return self._filter_items(receipt=receipt, **kwargs)

class TagFilter(object):
    """
    Filters items based on a tag.
    """

    def __init__(self, database):
        """
        Initialize self. See help(type(self)) for accurate signature.
        """
        self.database = database

    def _filter_items(self, *, path, criteria=tuple(), values=tuple(), **kwargs):
        """
        Retrieves receipt items from the database.
        """
        criteria = list(criteria)
        values = list(values)
        criteria.append('id in (SELECT item FROM Tag WHERE path LIKE ?)')
        values.append('{}%'.format(path))
        return self.database._filter_items(criteria=criteria, values=values, **kwargs)

    def __call__(self, *, path, **kwargs):
        """
        Retrieves receipt items from the database.
        """
        return self._filter_items(path=path, **kwargs)

class ItemTags(object):
    """
    Filters tags based on an item.
    """

    def __init__(self, database):
        """
        Initialize self. See help(type(self)) for accurate signature.
        """
        self.database = database

    def __call__(self, item):
        """
        Retrieves receipt items from the database.
        """
        assert isinstance(item, sqlite3.Row)
        cursor = self.database.connection.cursor()
        cursor.execute('SELECT path FROM Tag WHERE item in (SELECT id FROM Item WHERE id == ?)',
                       (item['id'],))
        return (t['path'] for t in FetchGenerator(cursor, 'path'))

class DateFilter(object):
    """
    Filters items based on their date.
    """

    def __init__(self, database):
        """
        Initialize self. See help(type(self)) for accurate signature.
        """
        self.database = database

    def _filter_items(self, *, date, criteria=tuple(), values=tuple(), **kwargs):
        """
        Retrieves receipt items from the database.
        """
        criteria = list(criteria)
        values = list(values)
        criteria.append('date == ?')
        values.append(date)
        return self.database._filter_items(criteria=criteria, values=values, **kwargs)

    def __call__(self, *, date, **kwargs):
        """
        Retrieves receipt items from the database.
        """
        return self._filter_items(date=date, **kwargs)
