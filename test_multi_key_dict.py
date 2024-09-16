import sys
import unittest
sys.path.append('../src/common')
print(sys.path)
from multi_key_dict import MultiKeyDict

class TestMultiKeyDict(unittest.TestCase):

    def setUp(self):
        self.mkd = MultiKeyDict(['id', 'name'], default_type_index='id')

    def test_init(self):
        self.assertIsInstance(self.mkd, MultiKeyDict)
        self.assertEqual(self.mkd._key_types, ['id', 'name'])
        self.assertEqual(self.mkd._default_type_index, 'id')

        # Test invalid initialization
        with self.assertRaises(ValueError):
            MultiKeyDict(['id', 'name'], default_type_index='age')

    def test_setitem(self):
        self.mkd[1, 'Alice'] = {'age': 30}
        self.assertEqual(self.mkd['id', 1], {'age': 30})
        self.assertEqual(self.mkd['name', 'Alice'], {'age': 30})
        self.assertEqual(self.mkd[1], {'age': 30})  # Using default key type

        # Test setting with default key type
        self.mkd[2] = {'age': 25}
        self.assertEqual(self.mkd[2], {'age': 25})

        # Test setting with invalid number of keys
        with self.assertRaises(ValueError):
            self.mkd['Alice'] = {'age': 30}  # Not enough keys
        with self.assertRaises(ValueError):
            self.mkd[1, 'Alice', 30] = {'age': 30}  # Too many keys

    def test_getitem(self):
        self.mkd[1, 'Alice'] = {'age': 30}
        self.assertEqual(self.mkd['id', 1], {'age': 30})
        self.assertEqual(self.mkd['name', 'Alice'], {'age': 30})
        self.assertEqual(self.mkd[1], {'age': 30})  # Using default key type

        with self.assertRaises(KeyError):
            self.mkd['id', 2]  # Non-existent key
        with self.assertRaises(KeyError):
            self.mkd['age', 30]  # Invalid key type
        with self.assertRaises(KeyError):
            self.mkd[('id', 1)]  # Invalid key format

    def test_delitem(self):
        self.mkd[1, 'Alice'] = {'age': 30}
        self.mkd[2, 'Bob'] = {'age': 25}

        del self.mkd['id', 1]
        with self.assertRaises(KeyError):
            self.mkd['id', 1]
        with self.assertRaises(KeyError):
            self.mkd['name', 'Alice']

        # Test deleting with default key type
        del self.mkd[2]
        with self.assertRaises(KeyError):
            self.mkd[2]

        # Test deleting non-existent key
        with self.assertRaises(KeyError):
            del self.mkd['id', 3]

    def test_iter(self):
        self.mkd[1, 'Alice'] = {'age': 30}
        self.mkd[2, 'Bob'] = {'age': 25}
        self.assertEqual(list(self.mkd), [1, 2])  # Should iterate over default key type

    def test_len(self):
        self.assertEqual(len(self.mkd), 0)
        self.mkd[1, 'Alice'] = {'age': 30}
        self.assertEqual(len(self.mkd), 1)
        self.mkd[2, 'Bob'] = {'age': 25}
        self.assertEqual(len(self.mkd), 2)

    def test_items(self):
        self.mkd[1, 'Alice'] = {'age': 30}
        self.mkd[2, 'Bob'] = {'age': 25}
        items = list(self.mkd.items())
        self.assertEqual(items, [(1, {'age': 30}), (2, {'age': 25})])

    def test_get(self):
        self.mkd[1, 'Alice'] = {'age': 30}
        self.assertEqual(self.mkd.get(('id', 1)), {'age': 30})
        self.assertEqual(self.mkd.get(1), {'age': 30})  # Using default key type
        self.assertEqual(self.mkd.get(('id', 2), 'Not found'), 'Not found')
        self.assertEqual(self.mkd.get(2, 'Not found'), 'Not found')  # Using default key type

    def test_update(self):
        other = {(1, 'Alice'): {'age': 30}, (2, 'Bob'): {'age': 25}}
        self.mkd.update(other)
        self.assertEqual(self.mkd['id', 1], {'age': 30})
        self.assertEqual(self.mkd['name', 'Bob'], {'age': 25})
        self.assertEqual(self.mkd[1], {'age': 30})  # Using default key type

        # Test updating with invalid keys
        with self.assertRaises(ValueError):
            self.mkd.update({('invalid',): {'age': 40}})

    def test_keys(self):
        self.mkd[1, 'Alice'] = {'age': 30}
        self.mkd[2, 'Bob'] = {'age': 25}
        self.assertEqual(set(self.mkd.keys('id')), {1, 2})
        self.assertEqual(set(self.mkd.keys('name')), {'Alice', 'Bob'})
        self.assertEqual(set(self.mkd.keys()), {1, 2})  # Using default key type

        with self.assertRaises(KeyError):
            self.mkd.keys('age')  # Invalid key type

    def test_values(self):
        self.mkd[1, 'Alice'] = {'age': 30}
        self.mkd[2, 'Bob'] = {'age': 25}
        self.assertEqual(list(self.mkd.values()), [{'age': 30}, {'age': 25}])

    def test_default_type_index(self):
        mkd = MultiKeyDict(['id', 'name'], default_type_index='name')
        mkd[1, 'Alice'] = {'age': 30}
        self.assertEqual(mkd['Alice'], {'age': 30})
        with self.assertRaises(KeyError):
            mkd[1]  # This should raise KeyError as 'id' is not the default key type

    def test_contains(self):
        self.mkd[1, 'Alice'] = {'age': 30}
        self.assertTrue(1 in self.mkd)
        self.assertTrue(('id', 1) in self.mkd)
        self.assertTrue(('name', 'Alice') in self.mkd)
        self.assertFalse(2 in self.mkd)
        self.assertFalse(('id', 2) in self.mkd)
        self.assertFalse(('name', 'Bob') in self.mkd)

    def test_clear(self):
        self.mkd[1, 'Alice'] = {'age': 30}
        self.mkd[2, 'Bob'] = {'age': 25}
        self.mkd.clear()
        self.assertEqual(len(self.mkd), 0)
        self.assertEqual(list(self.mkd.keys()), [])
        self.assertEqual(list(self.mkd.values()), [])

    def test_copy(self):
        self.mkd[1, 'Alice'] = {'age': 30}
        self.mkd[2, 'Bob'] = {'age': 25}
        mkd_copy = self.mkd.copy()
        self.assertEqual(mkd_copy['id', 1], {'age': 30})
        self.assertEqual(mkd_copy['name', 'Bob'], {'age': 25})
        self.assertEqual(mkd_copy._key_types, self.mkd._key_types)
        self.assertEqual(mkd_copy._default_type_index, self.mkd._default_type_index)

    def test_pop(self):
        self.mkd[1, 'Alice'] = {'age': 30}
        value = self.mkd.pop(1)
        self.assertEqual(value, {'age': 30})
        self.assertFalse(1 in self.mkd)
        self.assertFalse(('name', 'Alice') in self.mkd)

        with self.assertRaises(KeyError):
            self.mkd.pop(2)

        default = self.mkd.pop(2, 'default')
        self.assertEqual(default, 'default')

    def test_popitem(self):
        self.mkd[1, 'Alice'] = {'age': 30}
        item = self.mkd.popitem()
        self.assertEqual(item, (1, {'age': 30}))
        self.assertEqual(len(self.mkd), 0)

        with self.assertRaises(KeyError):
            self.mkd.popitem()

    def test_setdefault(self):
        value = self.mkd.setdefault(1, {'age': 30})
        self.assertEqual(value, {'age': 30})
        self.assertEqual(self.mkd[1], {'age': 30})

        value = self.mkd.setdefault(1, {'age': 25})
        self.assertEqual(value, {'age': 30})  # Original value is returned
        self.assertEqual(self.mkd[1], {'age': 30})  # Value is not changed

if __name__ == '__main__':
    unittest.main()
