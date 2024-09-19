import copy
import logging
from datetime import datetime
from multi_key_dict import MultiKeyDict


class MultiKeyDictCache():
    """
    MultiKeyDictCache is a class for managing a multi-key dictionary cache.
    
    This class provides functionality to create and manage a cache using multiple keys,
    allowing for flexible and efficient data retrieval.
    
    Attributes:
        _mkd_cache (MultiKeyDict): The main cache storage using MultiKeyDict.
        must_types_list (list): List of required key types for the cache.
        optional_types_list (list): List of optional key types for the cache.
        default_type (str or tuple): The default key type for the cache.
        _must_types_raw_names (set): Set of raw names for required key types.
        _optional_types_raw_names (set): Set of raw names for optional key types.
        _default_type_raw_name (set): Set of raw names for the default key type.
        _types_missing_flags (list): Flags indicating missing optional types.
        types_list (list): Combined list of all key types (must + optional).
        key_connector (str): String used to connect multiple keys.
    """
    def __init__(self, types_list, must_types_list, default_type, key_connector="__"):
        """
        Initializes the MultiKeyDictCache with specified parameters.

        Args:
            types_list (list): List of all key types for the cache.
            must_types_list (list, optional): List of required key types. Defaults to None.
            default_type (str or tuple, optional): The default key type. Defaults to None.
            key_connector (str, optional): String to connect multiple keys. Defaults to "__".
        """
        self._mkd_cache = None
        
        self.types_list = None
        self.must_types_list = None
        self.optional_types_list = None
        self.default_type = None
        
        self._must_types_raw_names= None
        self._optional_types_raw_names= None
        self._default_type_raw_name = None
        
        self._types_missing_flags = None

        self._set_types_list(must_types_list, types_list)
        self.set_default_type(default_type, init_flag=True)
        
        # Define class attribute
        key_connector = "__"
        self.key_connector = self._set_key_connector(key_connector) if key_connector else "__"
        # Set class attribute to match instance attribute
        MultiKeyDictCache.key_connector = self.key_connector


    def _set_key_connector(self, key_connector):
        """
        Initializes the key connector.
        """
        if not key_connector:
            raise ValueError(f"Key connector cannot be None or empty: {key_connector}.")
        
        if not isinstance(key_connector, str):
            raise ValueError(f"Key connector should be a string: {key_connector}.")
        
        return key_connector
        
    
    def _type_list_checker(self, raw_types_list):
        types_raw_names = []
        types_list = []
        for _type in raw_types_list:
            if type(_type) not in [list, tuple, str]:
                raise ValueError(f"Cache types should be a list, tuple or string: {types_list}.")
            
            if isinstance(_type, str):
                types_raw_names.append(_type)
                types_list.append(_type)
            
            elif len(_type) == 1:
                types_raw_names.append(_type[0])
                types_list.append(_type[0])
            
            elif isinstance(_type, list):
                types_raw_names.extend(_type)
                types_list.append(tuple(_type))

            else:
                types_raw_names.extend(list(_type))
                types_list.append(_type)
        
        return types_list, set(types_raw_names)

    
    def _set_types_list(self, raw_must_types_list, raw_types_list):
        """
        Initializes the cache columns list.

        Args:
            raw_must_types_list (list or tuple): List of required types.
            raw_types_list (list or tuple): List of all types.

        Raises:
            ValueError: If input lists are invalid.
        """
        # Validate input parameters
        if not raw_must_types_list:
            raise ValueError(f"must_types_list of MultiKeyDictCache cannot be None or empty: {raw_must_types_list}.")
        
        if not raw_types_list:
            raise ValueError(f"types_list of MultiKeyDictCache cannot be None or empty: {raw_types_list}.")
        
        if type(raw_must_types_list) not in [list, tuple]:
            raise ValueError(f"must_types_list of MultiKeyDictCache should be a list or tuple: {raw_must_types_list}.")
        
        if type(raw_types_list) not in [list, tuple]:
            raise ValueError(f"types_list of MultiKeyDictCache should be a list or tuple: {raw_types_list}.")
        
        def deduplicate(items):
            """
            Remove duplicates from a list while preserving order.
            """
            seen, result = set(), []
            for item in items:
                key = tuple(item) if isinstance(item, (list, tuple)) else item
                if key not in seen:
                    seen.add(key)
                    result.append(item)
            return result

        # Remove duplicates from input lists
        types_list = deduplicate(raw_types_list)
        must_types_list = deduplicate(raw_must_types_list)
        
        # Determine optional types
        optional_types_list = [item for item in types_list if item not in must_types_list]
                
        # Process must types and optional types
        self.must_types_list, self._must_types_raw_names = self._type_list_checker(types_list)
        self.optional_types_list, self._optional_types_raw_names = self._type_list_checker(optional_types_list) \
            if optional_types_list \
            else (None, None)
            
        # Combine must and optional types, set up missing flags
        if self.optional_types_list:
            self.types_list = self.must_types_list + self.optional_types_list
            self._types_missing_flags = [False] * len(self.optional_types_list)
        else:
            self.types_list = self.must_types_list
            self._types_missing_flags = []
            
        # Initialize the MultiKeyDict cache
        self._mkd_cache = MultiKeyDict(self.types_list, 0)
    
    def set_default_type(self, default_type, init_flag=False):
        """
        Sets the default type for the MultiKeyDict.
        
        Args:
            default_type (str or tuple): The default type for the MultiKeyDict.
        """
        default_type_raw_name = None

        if not default_type:
            raise ValueError(f"Default type cannot be None or empty: {default_type}.")
        
        if type(default_type) not in [str, tuple, list]:
            raise ValueError(f"Default type should be a string, tuple, or list: {default_type}.")
        
        if isinstance(default_type, str):
            default_type_raw_name = set([default_type])

        elif len(default_type) == 1:
            default_type_raw_name = set(default_type)
            default_type = default_type[0]
            
        else:
            default_type_raw_name = set(default_type)
            default_type = tuple(default_type)
            
        if default_type not in self.must_types_list:
            raise ValueError(f"Default type {default_type} is not in the types list: {self.must_types_list}")
        
        if not init_flag:
            self._previouse_default_type = self.default_type
        
        self.default_type = default_type
        self._default_type_raw_name = default_type_raw_name

        if self._mkd_cache:
            self._mkd_cache.set_default(self.must_types_list.index(default_type))
            

    def restore_default_type(self):
        """
        Restores the default type to the previous default type.
        """
        if not hasattr(self, "_previouse_default_type"):
            raise ValueError(f"Previous default type is not set: {self._previouse_default_type}")
        
        self.default_type = self._previouse_default_type
        if self._mkd_cache:
            self._mkd_cache.set_default(self.must_types_list.index(self.default_type))
        
            
    
    def _check_missing_keys(self, raw_dict = None):
        # Check if input is valid
        if not raw_dict or not isinstance(raw_dict, dict):
            raise ValueError(f"Input data to MkdCacheManager is None or not a dictionary: {raw_dict}")
        
        raw_keys = set(list(raw_dict.keys()))
        pop_msg = f"Cache %s is/are not in the row data: %s, row data: {raw_dict}"  
       
        # Check if default type keys are present
        if not raw_keys.issuperset(self._default_type_raw_name):
            logging.error(pop_msg% ("default key", self._default_type_raw_name - raw_keys))
            raise ValueError(pop_msg% ("self.default_type", self._default_type_raw_name - raw_keys))

        # Check if must type keys are present
        if not raw_keys.issuperset(self._must_types_raw_names):
            logging.error(pop_msg% ("self.must_types_list", self._must_types_raw_names - raw_keys), exc_info=True)
            raise ValueError(pop_msg% ("self.must_types_list", self._must_types_raw_names - raw_keys), exc_info=True)

        # Check for missing optional type keys
        if self._optional_types_raw_names and not raw_keys.issuperset(self._optional_types_raw_names):
            for index, _type in enumerate(self._optional_types_raw_names):
                if not raw_keys.issuperset(set(_type)):
                    self._types_missing_flags[index] = True
                    

    @classmethod
    def _process_value(cls, value):
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d-%H-%M-%S")
        elif isinstance(value, (list, tuple)):
            return tuple(value)
        elif isinstance(value, (int, float)):
            return str(value)
        elif value is None:
            return "None"
        else:
            return value


    @classmethod
    def generate_key(cls, row, key_name_list, exception_flag=True):
        """
        Generates a unique key for a given row based on specified key names.

        This method constructs a unique key for a row by concatenating the values of specified key names.
        It ensures that all key names are present in the row and that their values are not None.
        If any key name is missing or has a None value, the method logs a warning and returns None.

        Args:
            row (dict): The row data from which to generate the key.
            key_name_list (list): List of key names to use for generating the key.

        Returns:
            str: The generated key as a string, or None if the key cannot be generated.

        Raises:
            ValueError: If the input row is None or not a dictionary, or if the key_name_list is None or empty.

        Example:
            If row is {'stock_code': 'AAPL', 'trade_time': datetime(2023, 9, 1, 12, 0, 0)}
            and key_name_list is ['stock_code', 'trade_time'], 
            the generated key will be 'AAPL__2023-09-01-12-00-00'.
        """
        if not row or not isinstance(row, dict):
            msg = f"Input data to MkdCacheManager is None or not a dictionary: {row}"
            if exception_flag:
                raise ValueError(msg)
            logging.warning(msg)
            return None
        
        if not key_name_list:
            msg = f"Key name list cannot be None or empty: {key_name_list}"
            if exception_flag:
                raise ValueError(msg)
            logging.warning(msg)
            return None

        values = []
        for key_name in key_name_list:
            if key_name not in row:
                msg = f"Key name {key_name} is not in the row data: {row}"
                if exception_flag:
                    raise ValueError(msg)
                logging.warning(msg)
                return None
            values.append(cls._process_value(row[key_name]))

        return cls.key_connector.join(values)


    def _generate_query_keys(self, raw_dict):
        """
        Generates query keys based on the given query dictionary.
        
        Args:
            query_dict (dict): A dictionary containing query parameters.
        
        Returns:
            list: A list of possible query keys.
        """
        keys = []
        default_key = None
        for _type in self.types_list:
            if isinstance(_type, tuple):
                # Handle composite keys
                key_list = [raw_key if raw_key in raw_dict else None for raw_key in _type]
                if any([x is None for x in key_list]):
                    key = None
                    continue
                
                values = []
                for raw_key in _type:
                    if raw_key not in raw_dict:
                        key = None
                        break
                    values.append(MultiKeyDictCache._process_value(raw_dict[raw_key]))
                key = self.key_connector.join(values)
            else:
                # Handle single keys
                key = raw_dict.get(_type, None)

            if _type == self.default_type:
                default_key = key
            keys.append(key)
        return keys, default_key


    def _generate_upsert_keys(self, raw_dict):
        """
        Generates upsert keys for the given raw dictionary.

        This method first checks for any missing keys in the raw dictionary,
        then generates query keys and returns them as a tuple.

        Args:
            raw_dict (dict): The raw dictionary containing the data to be upserted.

        Returns:
            tuple: A tuple of generated upsert keys.
        """
        # Check for any missing keys in the raw dictionary
        self._check_missing_keys(raw_dict)
        
        # Generate query keys and convert the result to a tuple
        keys, default_key = self._generate_query_keys(raw_dict)
        return tuple(keys), default_key


    def upsert(self, dict_item):
        """
        Adds items to the cache.
        
        Args:
            items (dict): The items to add to the cache.
        """
        if not isinstance(dict_item, dict):
            raise ValueError(f"Input data to MkdCacheManager is not a dictionary: {dict_item}")
        
        mkd_keys, default_key = self._generate_upsert_keys(dict_item)
        if self.is_exists_by_key(default_key, self.default_type):
            self._mkd_cache[default_key].update(dict_item)
        else:
            self._mkd_cache[mkd_keys] = copy.deepcopy(dict_item)
        

    def upsert_by_default(self, dict_item, key):
        """
        Adds items to the cache using the default key.
        
        Args:
            items (dict): The items to add to the cache.
        """
        if not isinstance(dict_item, dict):
            raise ValueError(f"Input data to MkdCacheManager is not a dictionary: {dict_item}")
        
        if not key:
            raise ValueError(f"Key cannot be None or empty: {key}")
        
        if self.is_exists_by_key(key, self.default_type):
            self._mkd_cache[key].update(dict_item)
        else:
            self._mkd_cache[key] = copy.deepcopy(dict_item)


    def batch_upsert(self, dict_items):
        """
        Loads data from the table into the cache, sets the maximum ID value, and returns the queried data as a dictionary.
        
        Args:
            cache_filter (dict, optional): Filter criteria for loading data into cache.
        
        Returns:
            dict: The queried data with generated keys.
        """
        for dict_item in dict_items:
            self.upsert(dict_item)
            

    def fetch(self, key, type_name=None):
        """
        Fetches an item from the cache using the specified type_name and key.

        Args:
            type_name (str): The type name of the key.
            key (str): The key to fetch the item.

        Returns:
            dict: The fetched item if found, None otherwise.
        """
        try:
            if type_name is None:
                type_name = self.default_type
            value = self._mkd_cache[(type_name, key)]
            return copy.deepcopy(value)
        except KeyError:
            return None
        
 
    def query(self, sub_dict):
        """
        Queries the cache using a subset of the stored content dictionary.

        This method generates query keys, combines them with the types list,
        performs queries for each combination, and merges the results.

        Args:
            sub_dict (dict): A subset of the stored content dictionary to use for querying.

        Returns:
            list: A list of matching items from the cache.
        """
        query_keys, default_key = self._generate_query_keys(sub_dict)

        for _type, query_key in zip(self.types_list, query_keys):
            if not query_key:
                continue
            value = self.fetch(query_key, _type)
            if value is not None:
                return value
            
        return None
    

    def fetch_all(self, type_name=None):
        """
        Fetches all items from the cache.

        This method retrieves all items stored in the cache. If a type_name is provided,
        it temporarily sets the default type to the specified type before fetching.
        After fetching, it restores the original default type.

        Args:
            type_name (str, optional): The type name to set as default before fetching.
                                       If None, uses the current default type.

        Returns:
            dict: A deep copy of all items in the cache, where each key-value pair
                  represents a cached item.

        Note:
            - This method creates a deep copy of the cache to prevent modifications
              to the original cache data.
            - If a type_name is provided, the default type is temporarily changed
              and then restored after fetching.
        """
        if type_name:
            try:
                self.set_default_type(type_name)
            except ValueError as e:
                logging.error(f"Failed to set default type to {type_name}: {e}", exc_info=True)
                return {}

        rtn = {}
        for key, value in self._mkd_cache.items():
            rtn[key] = copy.deepcopy(value)
            
        if type_name:
            self.restore_default_type()
        
        return rtn
    

    def get_count(self, type_name=None, all_types=False):
        """
        Returns the number of items in the cache.
        
        Args:
            type_name (str, optional): The type name to get the count for.
        
        Returns:
            int: The number of items in the cache.
        """
        if type_name is None:
            type_name = self.default_type
            
        if all_types:
            return len(self._mkd_cache)
        
        return len(self._mkd_cache._indices[type_name])


    def is_exists_by_key(self, key, type_name=None):
        """
        Checks if the given key exists in the cache.
        
        Args:
            key (str): The key to check for existence.
        
        Returns:
            bool: True if the key exists in the cache, False otherwise.
        """
        if type_name is None:
            return key in self._mkd_cache
        return (type_name, key) in self._mkd_cache


    def is_exists(self, sub_dict):
        """
        Checks if the given sub_dict exists in the cache.
        
        Args:
            sub_dict (dict): The sub_dict to check for existence.
        
        Returns:
            bool: True if the sub_dict exists in the cache, False otherwise.
        """
        query_keys, default_key = self._generate_query_keys(sub_dict)
        for _type, query_key in zip(self.types_list, query_keys):
            if not query_key:
                continue
            if self.is_exists_by_key(query_key, _type):
                return True
        return False
