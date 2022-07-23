"""
Tests.
"""

import unittest
import datetime

from receiptsnatcher import (
    DatabaseLayer,
    BusinessFilter,
    ItemFilter,
    PriceFilter,
    ReceiptFilter,
    TagFilter,
    ItemTags,
    DateFilter,
    AndFilterClause,
    OrFilterClause,
)

class DatabaseTests(unittest.TestCase):
    """
    Tests for the DatabaseLayer.
    """

    today = datetime.date.today()

    def test_insert(self):
        """
        Tests the insert against its retrieval.
        """
        with DatabaseLayer(':memory:') as db:
            db.insert('business', b'test', DatabaseTests.today, 12.34, (
                {'name':'test float', 'price':1.34},
                {'name':'test integer', 'price':10},
                {'name':'test too many digits', 'price':1.00003}
            ))
            receipts = tuple(db.receipts)
            self.assertEqual(receipts[0]['business_name'], 'business')
            self.assertEqual(receipts[0]['image'], b'test')
            self.assertEqual(receipts[0]['total'], 12.34)
            items = tuple(db.items)
            self.assertEqual(items[0]['name'], 'test float')
            self.assertEqual(items[0]['price'], 1.34)
            self.assertEqual(items[0]['date'], DatabaseTests.today)
            self.assertEqual(items[1]['price'], 10.0)
            self.assertEqual(items[2]['price'], 1.0)

    def test_tagging(self):
        """
        Tests tagging logic.
        """
        with DatabaseLayer(':memory:') as db:
            db.insert('business', b'test', DatabaseTests.today, 12.34, (
                {'name':'test float', 'price':1.34},
                {'name':'test integer', 'price':10},
                {'name':'test too many digits', 'price':1.00003}
            ))
            items = tuple(db.items)
            db.add_tag(items[0], 'food / groceries')
            db.add_tag(items[1], 'food / groceries')
            tags = tuple(db.tags)
            self.assertEqual(tags[0]['item'], items[0]['id'])
            self.assertEqual(tags[0]['path'], 'food / groceries')
            self.assertEqual(tags[1]['item'], items[1]['id'])
            self.assertEqual(tags[1]['path'], 'food / groceries')
            db.remove_tag(items[0], 'food / groceries')
            self.assertEqual(tuple(db.tags)[0]['item'], items[1]['id'])

    def test_filters(self):
        """
        Tests filtering logic.
        """
        with DatabaseLayer(':memory:') as db:
            db.insert('business', b'test', DatabaseTests.today, 12.34, (
                {'name':'test float', 'price':1.34},
                {'name':'test integer', 'price':10},
                {'name':'test too many digits', 'price':1.00003}
            ))
            receipts = tuple(db.receipts)
            items = tuple(db.items)
            db.add_tag(items[0], 'food / groceries')
            db.add_tag(items[1], 'food / groceries')
            filter = BusinessFilter(db)
            self.assertEqual(filter('business'), receipts)
            filter = ItemFilter(db)
            self.assertEqual(filter(name='test integer'), items[1:2])
            filter = PriceFilter(db, limit=True)
            self.assertEqual(len(tuple(filter(price=5.0))), 2)
            filter = PriceFilter(db, limit=False)
            self.assertEqual(len(tuple(filter(price=1.1))), 2)
            filter = ReceiptFilter(db)
            self.assertEqual(filter(receipt=receipts[0]), items)
            filter = TagFilter(db)
            self.assertEqual(filter(path='food / groceries'), items[0:2])
            self.assertEqual(filter(path='food'), items[0:2])
            filter = ItemTags(db)
            self.assertEqual(tuple(filter(items[1]))[0], 'food / groceries')
            filter = DateFilter(db)
            self.assertEqual(filter(date=DatabaseTests.today), items)

    def test_layered_filters(self):
        """
        Tests filtering logic with filters layered on top of each other.
        """
        with DatabaseLayer(':memory:') as db:
            db.insert('business', b'test', DatabaseTests.today, 12.34, (
                {'name':'test float', 'price':1.34},
                {'name':'test integer', 'price':10},
                {'name':'test too many digits', 'price':1.00003}
            ))
            receipts = tuple(db.receipts)
            items = tuple(db.items)
            db.add_tag(items[0], 'food / groceries')
            db.add_tag(items[1], 'food / groceries')
            filter = ItemFilter(TagFilter(PriceFilter(DateFilter(ReceiptFilter(db)), limit=True)))
            self.assertEqual(filter(
                receipt=receipts[0],
                date=DatabaseTests.today,
                price=5.0,
                path='food',
                name='test float'
            ), items[0:1])

    def test_complex_filters(self):
        """
        Tests filtering logic with clauses (AND, OR).
        """
        with DatabaseLayer(':memory:') as db:
            db.insert('business', b'test', DatabaseTests.today, 12.34, (
                {'name':'test float', 'price':1.34},
                {'name':'test integer', 'price':10},
                {'name':'test too many digits', 'price':1.00003}
            ))
            receipts = tuple(db.receipts)
            items = tuple(db.items)
            db.add_tag(items[0], 'food / groceries')
            db.add_tag(items[1], 'food / groceries')
            filter = AndFilterClause(db, ItemFilter(None), TagFilter(None), PriceFilter(None, limit=True), DateFilter(None), ReceiptFilter(None))
            self.assertEqual(filter(
                receipt=receipts[0],
                date=DatabaseTests.today,
                price=5.0,
                path='food',
                name='test float'
            ), items[0:1])
            filter = OrFilterClause(db, AndFilterClause(db, ItemFilter(None), TagFilter(None), PriceFilter(None, limit=True)), DateFilter(None), ReceiptFilter(None))
            self.assertEqual(filter(
                receipt=receipts[0],
                date=DatabaseTests.today,
                price=5.0,
                path='food',
                name='test float'
            ), items)
