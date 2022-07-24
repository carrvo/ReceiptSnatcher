"""
Filters for receipt items.
"""

import sqlite3

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

class DateFilter(object):
    """
    Filters items based on their date.
    """

    def __init__(self, database):
        """
        Initialize self. See help(type(self)) for accurate signature.
        """
        self.database = database

    def _filter_items(self, *, lower_date_boundary=None, upper_date_boundary=None, criteria=tuple(), values=tuple(), **kwargs):
        """
        Retrieves receipt items from the database.
        """
        criteria = list(criteria)
        values = list(values)
        if lower_date_boundary is not None:
            criteria.append('date >= ?')
            values.append(lower_date_boundary)
        if upper_date_boundary is not None:
            criteria.append('date <= ?')
            values.append(upper_date_boundary)
        return self.database._filter_items(criteria=criteria, values=values, **kwargs)

    def __call__(self, *, lower_date_boundary=None, upper_date_boundary=None, **kwargs):
        """
        Retrieves receipt items from the database.
        """
        return self._filter_items(lower_date_boundary=lower_date_boundary, upper_date_boundary=upper_date_boundary, **kwargs)
