import unittest
from multi_key_dict_cache import MultiKeyDictCache

class TestMultiKeyDictCache(unittest.TestCase):

    def setUp(self):
        self.types_list = ['id', 'name', ('category', 'subcategory'), 'email']
        self.must_types_list = ['id', 'name']
        self.cache = MultiKeyDictCache(self.types_list, self.must_types_list, default_type='id')

    def test_init(self):
        self.assertIsInstance(self.cache, MultiKeyDictCache)
        self.assertEqual(self.cache.must_types_list, ['id', 'name'])
        self.assertEqual(self.cache.optional_types_list, [('category', 'subcategory'), 'email'])
        self.assertEqual(self.cache.default_type, 'id')

    def test_set_default_type(self):
        self.cache.set_default_type('name')
        self.assertEqual(self.cache.default_type, 'name')

        with self.assertRaises(ValueError):
            self.cache.set_default_type('invalid_type')

    def test_upsert(self):
        item = {
            'id': '1',
            'name': 'Test Item',
            'category': 'Test',
            'subcategory': 'Unit',
            'email': 'test@example.com'
        }
        self.cache.upsert(item)
        
        fetched_item, _ = self.cache.fetch('id', '1')
        self.assertEqual(fetched_item, item)

    def test_upsert_by_default(self):
        item = {
            'id': '2',
            'name': 'Default Item',
            'category': 'Test',
            'subcategory': 'Default',
            'email': 'default@example.com'
        }
        self.cache.upsert_by_default(item, '2')
        
        fetched_item, _ = self.cache.fetch('id', '2')
        self.assertEqual(fetched_item, item)

    def test_batch_upsert(self):
        items = [
            {
                'id': '3',
                'name': 'Item 3',
                'category': 'Test',
                'subcategory': 'Batch',
                'email': 'item3@example.com'
            },
            {
                'id': '4',
                'name': 'Item 4',
                'category': 'Test 4',
                'subcategory': 'Batch 4',
                'email': 'item4@example.com'
            }
        ]
        self.cache.batch_upsert(items)
        
        for item in items:
            fetched_item = self.cache.fetch('id', item['id'])
            self.assertEqual(fetched_item[0], item)

    def test_fetch(self):
        item = {
            'id': '5',
            'name': 'Fetch Test',
            'category': 'Test',
            'subcategory': 'Fetch',
            'email': 'fetch@example.com'
        }
        self.cache.upsert(item)
        
        fetched_item, _ = self.cache.fetch('id', '5')
        self.assertEqual(fetched_item, item)
        
        non_existent_item = self.cache.fetch('id', '999')
        self.assertEqual(non_existent_item, (None, None))

    def test_query(self):
        items = [
            {
                'id': '6',
                'name': 'Query Item 1',
                'category': 'Test',
                'subcategory': 'Query',
                'email': 'query1@example.com'
            },
            {
                'id': '7',
                'name': 'Query Item 2',
                'category': 'Test_',
                'subcategory': 'Query',
                'email': 'query2@example.com'
            }
        ]
        self.cache.batch_upsert(items)
        
        query_result = self.cache.query({'category': 'Test', 'subcategory': 'Query', 'id': '6', 'name': 'Query Item 1'})
        self.assertEqual(len(query_result), 2)
        
        query_result = self.cache.query({'name': 'Query Item 1'})
        self.assertEqual(query_result[0]['id'], '6')

    def test_is_exists(self):
        item = {
            'id': '8',
            'name': 'Exists Test',
            'category': 'Test',
            'subcategory': 'Exists',
            'email': 'exists@example.com'
        }
        self.cache.upsert(item)
        
        self.assertTrue(self.cache.is_exists('id', '8'))
        self.assertTrue(self.cache.is_exists('8'))
        self.assertFalse(self.cache.is_exists('id', '999'))
        self.assertFalse(self.cache.is_exists('999'))

if __name__ == '__main__':
    unittest.main()
