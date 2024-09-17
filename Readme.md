# MultiKeyDict

A dictionary that supports multiple key types for each value. Users must explicitly declare a default_type_index.

## Key Features

- Supports multiple key types for each value
- Requires explicit declaration of a default_type_index

## Installation
- None right now. just copy the code to yours.


## Internal structure

- _indices: Three-level structure: mkd_type -> mkd_key -> data_key
- _data: Two-level structure: data_key -> mkd_value
- _mkd_types: List of supported mkd_types
- _default_type_index: Index of the default mkd_type

## Method parameters

### Key-related parameter types

There are 6 kinds of key-related parameters used for different purposes in these methods:

1. type_index: An integer index or string key to specify a key type.
2. type_name: A string key to specify a key type.
3. mkd_keys: A tuple of mkd_key to specify a full set of keys.
4. mkd_key: A single mkd_key value.
5. type_key: A tuple of (mkd_type, mkd_key) to specify a key.
6. mkd_dict: A dictionary or an iterable of key/value pairs for updating the dictionary.

### Method-specific parameter usage

#### set_default
- Uses: type_index, type_name
- Note: It takes type_index by design, but type_name is also supported.

#### __setitem__
- Uses: mkd_keys
- Examples:
  1. Full key tuple:
     ```python
     >>> mkd[(1, 'AAPL', None)] = {'price': 150.0, 'volume': 1000000}
     ```
     This sets the value for 'table_id' and 'stock_code', but not for 'stock_name'.
  2. Simplified version:
     ```python
     >>> mkd[1] = {'price': 150.0, 'volume': 1000000}
     ```
     This sets the value for the default key type ('table_id').
- Note on default key type:
  ```python
  >>> mkd['AAPL'] = {'price': 150.0, 'volume': 1000000} # adds key to the default 'table_id' type
  >>> mkd.set_default('stock_code') # or mkd.set_default(1)
  >>> mkd['AAPL'] = {'price': 150.0, 'volume': 1000000} # now adds to 'stock_code' type
  ```

#### __getitem__
- Uses: type_key
- Format: tuple of (mkd_type, mkd_key) or list [mkd_type, mkd_key]
- Examples:
  ```python
  >>> mkd[['table_id', 1]]
  >>> mkd[('table_id', 1)]
  >>> mkd[1]  # uses default key type
  ```
  All return: {'price': 150.0, 'volume': 1000000}

#### __delitem__
- Uses: type_key
- Behavior: Similar to __getitem__

#### purge
- Uses: mkd_keys
- Behavior:
  - When 'deep' is False: Removes only the specific key type
  - When 'deep' is True: Removes all references to the key

#### __iter__, __len__, items, keys, values
- Uses: mkd_key
- Note: Uses the default key type when mkd_key is provided

#### update
- Uses: mkd_dict
- Format: Dictionary, MultiKeyDict object, or iterable of key/value pairs
- Note: Each key in mkd_dict is an mkd_keys

## Note

- The dictionary maintains internal indices for efficient lookup across different key types.
- The default_type_index is crucial for operations that work with a single key type.