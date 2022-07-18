"""
Tests.
"""

import unittest

from receiptsnatcher import DatabaseLayer

class DatabaseTests(unittest.TestCase):
    """
    Tests for the DatabaseLayer.
    """

    def test_insert(self):
        """
        Tests the insert against its retrieval.
        """
        with DatabaseLayer(':memory:') as db:
            db.insert('business', b'test', 12.34, (
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
            self.assertEqual(items[1]['price'], 10.0)
            self.assertEqual(items[2]['price'], 1.0)

    def test_tagging(self):
        """
        Tests adding a tag.
        """
        with DatabaseLayer(':memory:') as db:
            db.insert('business', b'test', 12.34, (
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
