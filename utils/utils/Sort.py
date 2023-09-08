class Sort:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Sort, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def sort_dict_list(self, dict_list, attribute, reverse=True, integer=False):
        if integer:
            sorted_list = sorted(dict_list, key=lambda x: float(x[attribute]), reverse=reverse)
        else:
            sorted_list = sorted(dict_list, key=lambda x: x[attribute].lower(), reverse=reverse)
        return sorted_list

    def sort_dict_by_keys(self, dictionary, reverse=False):
        return {key: dictionary[key] for key in sorted(dictionary, reverse=reverse)}

    def sort_dict_by_value(self, dictionary, reverse=True, integer=True):
        if integer:
            dictionary = {key: float(val) for key, val in dictionary.items()}
        sorted_items = sorted(dictionary.items(), key=lambda x: x[1], reverse=reverse)
        return {k: str(v) for k, v in sorted_items}

    def sort_dict_by_attribute_in_key(self, dictionary, attribute, integer=False):
        aux_dict = {int(val[attribute]): key for key, val in dictionary.items()} if integer else {val[attribute]: key for key, val in dictionary.items()}
        sorted_dict = self.sort_dict_by_keys(aux_dict)
        return {val: dictionary[val] for key, val in sorted_dict.items()}
