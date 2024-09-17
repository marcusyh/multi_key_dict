import copy
import logging
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
        self.set_default_type(default_type)
        
        self.key_connector = self._set_key_connector(key_connector) if key_connector else "__"
        

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

    
    def _set_types_list(self, must_types_list, types_list):
        """
        Initializes the cache columns list.
        """
        if not must_types_list:
            raise ValueError(f"must_types_list of MultiKeyDictCache cannot be None or empty: {must_types_list}.")
        
        if not types_list:
            raise ValueError(f"types_list of MultiKeyDictCache cannot be None or empty: {types_list}.")
        
        if type(must_types_list) not in [list, tuple]:
            raise ValueError(f"must_types_list of MultiKeyDictCache should be a list or tuple: {must_types_list}.")
        
        if type(types_list) not in [list, tuple]:
            raise ValueError(f"types_list of MultiKeyDictCache should be a list or tuple: {types_list}.")
        
        optional_types_list = []
        for _type in types_list:
            if _type not in must_types_list:
                optional_types_list.append(_type)
                
        self.must_types_list, self._must_types_raw_names = self._type_list_checker(must_types_list)
        self.optional_types_list, self._optional_types_raw_names = self._type_list_checker(optional_types_list) \
            if optional_types_list \
            else (None, None)
            
        self.types_list = self.must_types_list + self.optional_types_list if self.optional_types_list else self.must_types_list
        self._types_missing_flags = [False] * len(self.optional_types_list)
        
        self._mkd_cache = MultiKeyDict(self.types_list, 0)
       
    
    def set_default_type(self, default_type):
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
            default_type = default_type
            default_type_raw_name = {default_type}

        elif len(default_type) == 1:
            default_type = default_type[0]
            default_type_raw_name = {default_type[0]}
            
        else:
            default_type = tuple(default_type)
            default_type_raw_name = set(default_type)
            
        if default_type not in self.must_types_list:
            raise ValueError(f"Default type {default_type} is not in the types list: {self.must_types_list}")
        
        self.default_type = default_type
        self._default_type_raw_name = default_type_raw_name

        if self._mkd_cache:
            self._mkd_cache.set_default(self.must_types_list.index(default_type))
            
    
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
            logging.error(pop_msg% ("self.must_types_list", self._must_types_raw_names - raw_keys))
            raise ValueError(pop_msg% ("self.must_types_list", self._must_types_raw_names - raw_keys))

        # Check for missing optional type keys
        if not raw_keys.issuperset(self._optional_types_raw_names):
            for index, _type in enumerate(self._optional_types_raw_names):
                if not raw_keys.issuperset(set(_type)):
                    self._types_missing_flags[index] = True
        

    def _generate_query_keys(self, raw_dict):
        """
        Generates query keys based on the given query dictionary.
        
        Args:
            query_dict (dict): A dictionary containing query parameters.
        
        Returns:
            list: A list of possible query keys.
        """
        keys = []
        for _type in self.types_list:
            if isinstance(_type, tuple):
                # Handle composite keys
                key_list = [raw_key if raw_key in raw_dict else None for raw_key in _type]
                if any([x is None for x in key_list]):
                    key = None
                    continue
                key = self.key_connector.join([str(x) for x in [raw_dict[raw_key] for raw_key in _type]])
            else:
                # Handle single keys
                key = raw_dict.get(_type, None)
            keys.append(key)
        return keys


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
        return tuple(self._generate_query_keys(raw_dict))


    def upsert(self, dict_item):
        """
        Adds items to the cache.
        
        Args:
            items (dict): The items to add to the cache.
        """
        if not isinstance(dict_item, dict):
            raise ValueError(f"Input data to MkdCacheManager is not a dictionary: {dict_item}")
        
        mkd_keys = self._generate_upsert_keys(dict_item)
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
            

    def fetch(self, type_name, key):
        """
        Fetches an item from the cache using the specified type_name and key.

        Args:
            type_name (str): The type name of the key.
            key (str): The key to fetch the item.

        Returns:
            dict: The fetched item if found, None otherwise.
        """
        try:
            return self._mkd_cache[(type_name, key)]
        except KeyError:
            return None, None

 
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
        query_keys = self._generate_query_keys(sub_dict)

        results = {}
        for _type, query_key in zip(self.types_list, query_keys):
            if not query_key:
                continue
            value, inner_key = self.fetch(_type, query_key)
            if not inner_key:
                continue
            if inner_key not in results:
                results[inner_key] = {
                    "value": value,
                    "count": 0
                }
            results[inner_key]["count"] += 1
            
        if results:
            results = sorted(results.items(), key=lambda x: x[1]["count"], reverse=True)
            inner_key, result = results[0]
            return result["value"], inner_key
        return None, None


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
        query_keys = self._generate_query_keys(sub_dict)
        for _type, query_key in zip(self.types_list, query_keys):
            if not query_key:
                continue
            if self.is_exists_by_key(query_key, _type):
                return True
        return False