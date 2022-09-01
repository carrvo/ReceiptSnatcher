"""
Filters for tags.
"""

import sqlite3

class ItemTags(object):
    """
    Filters tags based on an item.
    """

    def __init__(self, database):
        """
        Initialize self. See help(type(self)) for accurate signature.
        """
        self.database = database

    def _filter_tags(self, *, item, criteria=tuple(), values=tuple(), **kwargs):
        """
        Retrieves tags from the database.
        """
        criteria = list(criteria)
        values = list(values)
        assert isinstance(item, sqlite3.Row)
        criteria.append('item in (SELECT id FROM Item WHERE id == ?)')
        values.append(item['id'])
        return self.database._filter_tags(criteria=criteria, values=values, **kwargs)

    def __call__(self, *, item, **kwargs):
        """
        Retrieves tags from the database.
        """
        return (t['path'] for t in self._filter_tags(item=item, **kwargs))
