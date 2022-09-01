"""
Filters for receipt transactions.
"""

class BusinessFilter(object):
    """
    Filters receipts based on their business name.
    """

    def __init__(self, database):
        """
        Initialize self. See help(type(self)) for accurate signature.
        """
        self.database = database

    def _filter_receipts(self, *, name, criteria=tuple(), values=tuple(), **kwargs):
        """
        Retrieves receipt transactions from the database.
        """
        criteria = list(criteria)
        values = list(values)
        criteria.append('business_name == ?')
        values.append(name)
        return self.database._filter_receipts(criteria=criteria, values=values, **kwargs)

    def __call__(self, *, name, **kwargs):
        """
        Retrieves receipt transactions from the database.
        """
        return self._filter_receipts(name=name, **kwargs)
