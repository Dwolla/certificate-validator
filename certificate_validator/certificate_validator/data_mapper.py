"""
Data Mapper class.
"""


class DataMapperValue:
    """
    Data Mapper Value.
    """
    def __init__(self, param: str, default='', parser=None):
        """
        Construct Data Mapper Value.
        """
        self.param = param
        self.default = default
        self._parser = parser

    def parsed(self, value):
        """
        Return Parsed Value.
        """
        if self._parser and callable(self._parser):
            return self._parser(value)
        return value


class CleanListValue(DataMapperValue):
    """
    Clean List Data Mapper Value.
    """
    def __init__(self, param, invalid_values=None):
        """
        Construct Clean List Data Mapper Value Definition.
        """
        super().__init__(param)
        self.invalid_values = invalid_values if invalid_values else [
            None, '', '-'
        ]

    def parsed(self, value):
        """
        Parse Value.
        """
        if not value:
            value = []
        return [item for item in value if item not in self.invalid_values]


class ClassValue(DataMapperValue):
    """
    Data Mapper Value that expects a child DataMapper class as value.
    """
    def __init__(self, param, clazz, default=None):
        """
        Construct Class Data Mapper Value.
        """
        super().__init__(param, default=default)
        self.clazz = clazz

    def parsed(self, value):
        """
        Parse Value.
        """
        if not value:
            value = {}
        return self.clazz(**value)


class DataMapper:
    """
    Base class for data mapped classes.
    """
    MAP = {}

    def __init__(self, **kwargs):
        """
        Construct a data map from a dictionary.
        """
        data = {}

        # Add Defaults
        for param_name, param in self.MAP.items():
            data[param_name] = param.default

        # add values
        data.update(kwargs)

        # Load parameters
        for param_name, value in data.items():
            param = self.MAP.get(param_name, None)
            if param and isinstance(param, DataMapperValue):
                param_name = param.param
                value = param.parsed(value)
            self.__dict__[param_name] = value
