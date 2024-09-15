class MultiKeyDict:
    """
        This dictionary supports multiple key types for each value. Users must explicitly declare a default_type_index.

        Key features:
        - Supports multiple key types for each value
        - Requires explicit declaration of a default_type_index

        Example:
        >>> mkd = MultiKeyDict(['table_id', 'stock_code', 'stock_name'], default_type_index=0)
        >>> mkd[(1, 'AAPL', 'Apple Inc.')] = {'price': 150.0, 'volume': 1000000}
        >>> mkd[(2, 'GOOG', 'Alphabet Inc.')] = {'price': 1200.0, 'volume': 500000}
        >>> # We can now get the value using any of the key types
        >>> mkd['table_id', 1]
        {'price': 150.0, 'volume': 1000000}
        >>> mkd['stock_code', 'AAPL']
        {'price': 150.0, 'volume': 1000000}
        >>> mkd['stock_name', 'Apple Inc.']
        {'price': 150.0, 'volume': 1000000}
        >>> mkd.set_default('stock_code')
        >>> mkd['AAPL']
        {'price': 150.0, 'volume': 1000000}
        >>> mkd.set_default(2)
        >>> mkd['Alphabet Inc.']
        {'price': 1200.0, 'volume': 500000}
        >>> mkd.update({(3, 'MSFT', 'Microsoft Corp.'): {'price': 200.0, 'volume': 800000}})

        Naming convention:
        - As it's a 3-level dictionary, we use the following terms from the user's perspective:
            - mkd_type: The type of key (e.g., 'table_id', 'stock_code')
            - mkd_key: The actual key value for a specific mkd_type
            - mkd_value: The value associated with a set of keys
        - To understand the internal structure, we use the following terms:
            - _indices: Three-level structure: mkd_type -> mkd_key -> data_key
            - _data: Two-level structure: data_key -> mkd_value
            - _mkd_types: Internal list of supported mkd_types
            - data_key: The full set of keys used internally to store values

        Method parameters:
        - There are 5 kinds of key-related parameters used for different purposes in these methods:
            - type_index: A single index or key to specify a key type.
            - type_name: A single key to specify a key type.
            - mkd_keys: A tuple of mkd_key to specify a full set of keys.
            - mkd_key: A single mkd_key value.
            - type_key: A tuple of (mkd_type, mkd_key) to specify a key.
            - mkd_dict: A dictionary or an iterable of key/value pairs for updating the dictionary.
        
        - Method parameters and their corresponding key types:
            - set_default: 
                - type_index, type_name. It takes type_index by desgined, but type_name is also supported.
            - __setitem__: 
                - mkd_keys is used. 
                An example:
                >>> mkd[(1, 'AAPL', None)] = {'price': 150.0, 'volume': 1000000}
                This will set the value for 'table_id' and 'stock_code', but not for 'stock_name'. 
                It looks like the table_id sub dictionary and the stock_code sub dictionary has the 
                stock infomation value, but the stock_name sub dictionary dont have the value.
                - A simplified version of mkd_keys  is also supported.
                An example:
                >>> mkd[1] = {'price': 150.0, 'volume': 1000000}
                This method will set the value for 'table_id' the default key type, the value can be
                get by the 'table_id' key type, but can not be get by the 'stock_code' or 'stock_name' key type.
                - Note:
                By the second simplified way, the default key type is used to define which type is used, and the
                key is always added to the default key type. For exmple:
                >>> mkd['AAPL'] = {'price': 150.0, 'volume': 1000000} # will also add the key to the 'table_id' key type.
                To add the key to the 'stock_code' key type, you should use the full key tuple, the first way, or you 
                need to change the default type by the set_default method.
                >>> mkd.set_default('stock_code') # or mkd.set_default(1)
                >>> mkd['AAPL'] = {'price': 150.0, 'volume': 1000000}
            - __getitem__:
                - type_key is used.
                type_key is a tuple of (mkd_type, mkd_key) or list [mkd_type, mkd_key] to specify a key.
                the first element mkd_type can be omitted if the default key type is set.
                when the first element mkd_type is omitted, the type_key should not be a list or tuple, just
                use the mkd_key directly.
                An example:
                >>> mkd[['table_id', 1]]
                {'price': 150.0, 'volume': 1000000}
                >>> mkd[('table_id', 1)]
                {'price': 150.0, 'volume': 1000000}
                >>> mkd[1]
                {'price': 150.0, 'volume': 1000000}
                All the above will return the value for the 'table_id' key type, they are the same.
                The third way parameter, we also call it mkd_key.
            __delitem__:
                - type_key is used.
                simmilar to the __getitem__ method.
            purge:
                - mkd_keys is used.
                simmilar to the __setitem__ method.
                when 'deep' is False, the method will only remove the specific key type, and maintain other key types if possible.
                when 'deep' is True, the method will remove all references to the key.
            __iter__, __len__, items, keys, values:
                - mkd_key is used.
                mkd_key is a single mkd_key value, a mkd_key value is a value of a specific mkd_type. it looks the same as the python
                internal dict.
                when a mkd_key as parameter, the default key type is used to get the value.
            update:
                - mkd_dict is used.
                mkd_dict is a dictionary or an MultiKeyDict object, or an iterable of key/value pairs.
                key of each element in the mkd_dict is a mkd_keys.
                    
        Note:
        - The dictionary maintains internal indices for efficient lookup across different key types.
        - The default_type_index is crucial for operations that work with a single key type.
        """
    def __init__(self, mkd_types, default_type_index):
        """
        Initialize a MultiKeyDict instance.
        Init args:
            mkd_types (list): List of key types supported by this dictionary.
            default_type_index (int or str): The default key type to use when a single key is provided.
                Can be either an index of mkd_types or a string matching one of the mkd_types.
        """
        self._data = {}  # Main storage for data_key -> mkd_value pairs
        self._indices = {mkd_type: {} for mkd_type in mkd_types}  # Indices for quick lookup
        self._mkd_types = mkd_types  # List of supported mkd_types
        self._default_type_index = None
        self.set_default(default_type_index)  # Set the default mkd_type
       
    def _normalize_keys(self, mkd_keys):
        """
        Normalize input keys to a tuple of the correct length.
        
        If a single key is provided and a default mkd_type exists,
        it will be paired with the default mkd_type.

        This method works with all mkd_types.

        Args:
            mkd_keys: The input mkd_key or keys.

        Returns:
            tuple: Normalized data_key.

        Raises:
            ValueError: If the number of keys doesn't match the expected number.

        Note:
        - This method is crucial for maintaining consistency in key formats throughout the dictionary.
        - It handles both single key inputs (when a default type is set) and full key tuples.
        """
        # Check if mkd_keys is already in the correct format
        if isinstance(mkd_keys, tuple) and len(mkd_keys) == len(self._mkd_types):
            return mkd_keys

        # Handle the case when a default type index is set
        if self._default_type_index is not None:
            if self._is_single_key(mkd_keys):
                return self._create_full_key_tuple(mkd_keys)

        # Raise an error if the number of keys doesn't match
        raise ValueError(f"Expected {len(self._mkd_types)} keys, got {len(mkd_keys) if isinstance(mkd_keys, tuple) else 1}")

    def _is_single_key(self, mkd_keys):
        """
        Check if mkd_keys is a single key or a tuple with one element.

        Args:
            mkd_keys: The input key or keys to check.

        Returns:
            bool: True if mkd_keys is a single key, False otherwise.

        Note:
        - This helper method is used in key normalization to determine if a default type should be applied.
        """
        return (isinstance(mkd_keys, (int, str, float, bool)) or
                (isinstance(mkd_keys, tuple) and len(mkd_keys) == 1))

    def _create_full_key_tuple(self, mkd_keys):
        """
        Create a full key tuple using the default type index.

        Args:
            mkd_keys: The input key or keys.

        Returns:
            tuple: A full key tuple with the input key at the default type index and None for other positions.

        Note:
        - This method is used when a single key is provided and a default type is set.
        - It creates a full key tuple compatible with the dictionary's internal structure.
        """
        return tuple(mkd_keys if idx == self._default_type_index else None
                     for idx in range(len(self._mkd_types)))

    def _parse_key(self, input_type_key):
        """
        Parse a mkd_key or key tuple into a standardized format.
        
        Returns a tuple of (mkd_type, mkd_key).

        This method works with all mkd_types.

        Args:
            input_type_key: The input key to parse.

        Returns:
            tuple: A tuple containing (mkd_type, mkd_key).

        Raises:
            KeyError: If the key format is invalid.

        Note:
        - This method handles various input formats, including single keys, tuples, and index-based keys.
        - It's essential for maintaining consistency in how keys are interpreted throughout the dictionary.
        """
        input_type = type(input_type_key)
        
        if input_type not in [int, str, float, bool, list, tuple]:
            raise KeyError("Invalid key format")

        if input_type in [list, tuple] and len(input_type_key) != 2:
            raise KeyError("Invalid key format")
        
        if input_type in [int, str, float, bool] and self._default_type_index is not None:
            return self._mkd_types[self._default_type_index], input_type_key
        
        mkd_type, mkd_key = input_type_key
        if mkd_type in self._mkd_types:
            return mkd_type, mkd_key
        
        # if mkd_type is an integer, assume it's an index
        if isinstance(mkd_type, int) and 0 <= mkd_type < len(self._mkd_types):
            return self._mkd_types[mkd_type], mkd_key
            
        raise KeyError("Invalid key format")
    

    def _check_conflicating_keys(self, data_key):
        """
        Check for conflicting and updating keys in the dictionary.

        Args:
            data_key: The key to check for conflicts.

        Returns:
            tuple: Two lists - conflicting keys and updating keys.

        Note:
        - This method is crucial for maintaining data integrity when inserting or updating values.
        - It identifies both conflicting keys (which would overwrite existing data) and updating keys (which need to be merged).
        """
        related_data_keys = []
        for mkd_type, mkd_key in zip(self._mkd_types, data_key):
            if mkd_key is None:
                continue
            if mkd_key not in self._indices[mkd_type]:
                continue
            related_data_keys.append(self._indices[mkd_type].get(mkd_key))
            
        conflicting = []
        updating = []
        for exists_data_key in related_data_keys:
            conflict_flag = False
            for k1, k2 in zip(data_key, exists_data_key):
                if k1 is not None and k2 is not None and k1 != k2:
                    conflicting.append(exists_data_key)
                    conflict_flag = True
                    break
            if not conflict_flag and exists_data_key != data_key:
                updating.append(exists_data_key)

        return conflicting, updating
        
    
    def _get_new_data_key(self, data_key, updating):
        """
        Generate a new data key by merging the input key with updating keys.

        Args:
            data_key: The input data key.
            updating: List of keys that need to be updated.

        Returns:
            tuple: A new data key that combines information from the input and updating keys.

        Note:
        - This method is used when updating existing entries to ensure all relevant key information is preserved.
        - It prioritizes non-None values when merging keys.
        """
        new_data_key = []
        for index in range(len(self._mkd_types)):
            for key in [data_key[index] for data_key in updating + [data_key]]:
                if key is not None:
                    new_data_key.append(key)
                    break
            else:
                new_data_key.append(None)
        return tuple(new_data_key)
 

    def __setitem__(self, mkd_keys, mkd_value):
        """
        Set an item in the dictionary.

        This method works with all mkd_types.

        Args:
            mkd_keys: The mkd_key or keys to set.
            mkd_value: The value to set.

        Raises:
            ValueError: If conflicting keys are found.

        Note:
        - This method handles the complexities of setting items in a multi-key dictionary.
        - It checks for conflicts, updates existing entries if necessary, and maintains the internal indices.
        """
        data_key = self._normalize_keys(mkd_keys)
        print(data_key)
        
        conflicting_keys, updating_keys = self._check_conflicating_keys(data_key)
        print(conflicting_keys, updating_keys)
        if conflicting_keys:
            raise ValueError(f"Conflicting key found for {data_key}: {conflicting_keys}")

        if updating_keys:
            data_key = self._get_new_data_key(data_key, updating_keys)
            for exists_data_key in updating_keys:
                del self._data[exists_data_key]

        self._data[data_key] = mkd_value
        
        # Update all indices
        for mkd_type, mkd_key in zip(self._mkd_types, data_key):
            if mkd_key is None:
                continue
            self._indices[mkd_type][mkd_key] = data_key


    def __getitem__(self, type_key):
        """
        Get an item from the dictionary.

        This method works with all mkd_types.

        Args:
            mkd_key: The mkd_key to look up.

        Returns:
            The mkd_value associated with the key.

        Raises:
            KeyError: If the key is not found.

        Note:
        - This method uses the internal indices for efficient lookup across different key types.
        """
        mkd_type, mkd_key = self._parse_key(type_key)
        data_key = self._indices[mkd_type][mkd_key]
        return self._data[data_key]


    def __delitem__(self, type_key, deep=False):
        """
        Delete an item from the dictionary.

        Args:
            type_key: The key to delete.
            deep (bool): If True, remove all references to the key. If False, only remove the specific key type.

        Note:
        - This method delegates to the 'purge' method for actual deletion.
        - The 'deep' parameter determines whether to remove all references or just the specific key type.
        """
        mkd_type, mkd_key = self._parse_key(type_key)
        data_key = tuple([mkd_key if mkd_type == mkd_type_ else None for mkd_type_ in self._mkd_types])
        self.purge(data_key, deep)


    def purge(self, mkd_keys, deep=True):
        """
        Remove an item from the dictionary and update indices accordingly.

        Args:
            mkd_keys: The key(s) of the item to remove.
            deep (bool): If True, remove all references to the key. If False, maintain other key types if possible.

        Raises:
            ValueError: If conflicting keys are found.
            KeyError: If the key is not found in the dictionary.

        Note:
        - This method handles the complexities of removing items from a multi-key dictionary.
        - It updates internal indices and handles partial key deletions when 'deep' is False.
        """
        print(mkd_keys, 1)
        data_key = self._normalize_keys(mkd_keys)
        
        print(data_key, 2)
        conflicting_keys, updating_keys = self._check_conflicating_keys(data_key)
        print(conflicting_keys, updating_keys, 3)
        print(self._data, 4)
        if conflicting_keys:
            raise ValueError(f"Conflicting key found for {data_key}: {conflicting_keys}")
        
        if updating_keys:
            for exists_data_key in updating_keys:
                exists_data_key = tuple(exists_data_key)
                print(exists_data_key)
                mkd_value = self._data[exists_data_key]
                del self._data[exists_data_key]
            full_data_key = self._get_new_data_key(data_key, updating_keys)
        else:
            if data_key not in self._data:
                raise KeyError(f"Key not found: {data_key}")
            del self._data[data_key]
            full_data_key = data_key
        print(self._data, 5)
        print(full_data_key, 6)
        
        print(self._indices, 7)
        if deep:
            for mkd_type, mkd_key in zip(self._mkd_types, full_data_key):
                if mkd_key is not None and mkd_key in self._indices[mkd_type]:
                    del self._indices[mkd_type][mkd_key]
            print(self._indices, 8)
            return

        if updating_keys:
            new_data_key = [k1 if k1 != k2 and k1 is not None else None for k1, k2 in zip(full_data_key, data_key)]
        else:
            new_data_key = [None]*len(data_key)
            
        # Update all indices
        print(data_key, new_data_key, 9.1)
        for mkd_type, mkd_key, new_mkd_key in zip(self._mkd_types, data_key, new_data_key):
            if new_mkd_key is not None:
                self._indices[mkd_type][new_mkd_key] = new_data_key
                self._data[tuple(new_data_key)] = mkd_value
                print(new_data_key, 9.2)
                continue
            if mkd_key in self._indices[mkd_type]:
                print(mkd_key, 9.3)
                del self._indices[mkd_type][mkd_key]
        
        print(self._indices, 9.4)
        print(self._data, 9.5)
                

    def __iter__(self):
        """
        Return an iterator over the dictionary's keys for the default mkd_type.

        This method only works with the default mkd_type.

        Returns:
            An iterator over the dictionary's keys for the default mkd_type.

        Note:
        - This method is designed to work only with the default key type for consistency with standard dict behavior.
        """
        return iter(self._indices[self._mkd_types[self._default_type_index]])

    def __len__(self):
        """
        Return the number of items in the dictionary for the default mkd_type.

        This method only works with the default mkd_type.

        Returns:
            int: The number of items in the dictionary for the default mkd_type.

        Note:
        - The length is based on the number of keys in the default key type index.
        """
        return len(self._indices[self._mkd_types[self._default_type_index]])

    def items(self):
        """
        Return a view of the dictionary's items for the default mkd_type.

        This method only works with the default mkd_type.

        Returns:
            A view object of the dictionary's (mkd_key, mkd_value) pairs for the default mkd_type.
        """
        default_type = self._mkd_types[self._default_type_index]
        return {k: self._data[v] for k, v in self._indices[default_type].items()}.items()

    def get(self, mkd_key, default=None):
        """
        Get an item from the dictionary, returning a default value if the key is not found.

        This method works with all mkd_types.

        Args:
            key: The mkd_key to look up.
            default: The value to return if the key is not found (default is None).

        Returns:
            The mkd_value associated with the key, or the default value if the key is not found.
        """
        try:
            return self[mkd_key]
        except KeyError:
            return default

    def update(self, mkd_dict, force=False):
        """
        Update the dictionary with the key/value pairs from another dictionary or iterable.

        This method works with all mkd_types.

        Args:
            other: Another dictionary or an iterable of key/value pairs.
            force (bool): If True, ignore conflicting keys and update other items. If False, raise an exception on conflicts.

        Raises:
            TypeError: If 'other' is not a dictionary or iterable of key/value pairs.
            ValueError: If conflicting keys are found and force is False.
        """
        if isinstance(mkd_dict, dict):
            items = mkd_dict.items()
        elif hasattr(mkd_dict, '__iter__'):
            items = mkd_dict
        else:
            raise TypeError(f"Expected a dictionary or iterable, got {type(mkd_dict).__name__}")

        conflicts = []
        update_indices = {}
        update_normally = {}

        for mkd_keys, mkd_value in items:
            normalized_keys = self._normalize_keys(mkd_keys)
            
            # Check for conflicts with existing keys
            conflicting_keys, updating_keys  = self._check_conflicating_keys(normalized_keys)
            if conflicting_keys:
                conflicts.append((normalized_keys, conflicting_keys))
                continue
            
            if updating_keys:
                new_data_key = self._get_new_data_key(normalized_keys, updating_keys) 
                for exists_data_key in updating_keys:
                    update_indices[new_data_key] = [exists_data_key, mkd_value]
                continue
            
            update_normally[normalized_keys] = mkd_value

        print(conflicts, update_indices, update_normally)
        if conflicts:
            print(f"Warning: Conflicting key found between new elements and exists elements: ")
            for conflict in conflicts:
                print(f"{conflict[0]} : {conflict[1]}")
            if not force:
                raise ValueError(f"Conflicting key found")

        # Check for conflicts within the new keys
        conflicts = []
        duplicates = []
        checking_list = list(update_indices.keys())+list(update_normally.keys())
        print(conflicts, duplicates, checking_list)
        skip_list = [False]*len(checking_list)
        for i, keys1 in enumerate(checking_list):
            for keys2 in list(checking_list)[i+1:]:
                if not any(k1 is not None and k2 is not None and k1 == k2 for k1, k2 in zip(keys1, keys2)):
                    continue
                if keys1 == keys2:
                    duplicates.append(keys1, keys2)
                    skip_list[i+1] = True
                else:
                    conflicts.append((keys1, keys2))
                    skip_list[i] = True
                    skip_list[i+1] = True
        update_normally_new = {}
        for key, flag in zip(checking_list, skip_list):
            if flag:
                continue
            if key not in update_normally:
                continue
            update_normally_new[key] = update_normally[key]
        update_normally = update_normally_new
        if conflicts or duplicates:
            print(f"Warning: Conflicting or duplicate key found between new elements: ")
            for conflict in conflicts:
                print(f"Conflicting: {conflict[0]} : {conflict[1]}")
            for duplicate in duplicates:
                print(f"Conflicting: {duplicate[0]} : {duplicate[1]}")
            if not force:
                raise ValueError(f"Conflicting or duplicate key found")


        print(update_indices, update_normally)
        # Perform the update
        for data_key, tmp in update_indices.items():
            exists_data_key, mkd_value = tmp
            exists_data_key = tuple(exists_data_key)
            del self._data[exists_data_key]
            update_normally[data_key] = mkd_value
            
        print(update_normally)
        for data_key, mkd_value in update_normally.items():
            for mkd_type, mkd_key in zip(self._mkd_types, data_key):
                if mkd_key is None:
                    continue
                self._indices[mkd_type][mkd_key] = data_key
            self._data[data_key] = mkd_value
            
        print(self._data)
        print(self._indices)


    def keys(self, mkd_type=None):
        """
        Return a view of the dictionary's keys for the default mkd_type or specified mkd_type.

        This method can work with all mkd_types if a specific mkd_type is provided.
        If no mkd_type is provided, it works with the default mkd_type.

        Args:
            mkd_type (optional): If provided, return keys of this specific type.
                                 If not provided, use the default mkd_type.

        Returns:
            A view object of the dictionary's mkd_keys for the specified or default mkd_type.

        Raises:
            KeyError: If an invalid mkd_type is provided.
        """
        if mkd_type is None:
            mkd_type = self._mkd_types[self._default_type_index]
        if mkd_type not in self._indices:
            raise KeyError(f"Invalid key type: {mkd_type}")
        return self._indices[mkd_type].keys()

    def values(self):
        """
        Return a view of the dictionary's values for the default mkd_type.

        This method only works with the default mkd_type.

        Returns:
            A view object of the dictionary's mkd_values for the default mkd_type.
        """
        default_type = self._mkd_types[self._default_type_index]
        return (self._data[v] for v in self._indices[default_type].values())
    
    def set_default(self, mkd_type_index):
        """
        Set the default mkd_type for the dictionary.

        This method affects operations that work with the default mkd_type.

        Args:
            mkd_type_index: The mkd_type to set as default. Can be a mkd_type or an index.

        Raises:
            KeyError: If an invalid mkd_type is provided.
        """
        if isinstance(mkd_type_index, int) and 0 <= mkd_type_index < len(self._mkd_types):
            self._default_type_index = mkd_type_index
            return
        if mkd_type_index in self._mkd_types:
            self._default_type_index = self._mkd_types.index(mkd_type_index)
            return
        raise KeyError(f"Invalid default key type: {mkd_type_index}")