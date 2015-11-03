from flask import request


class Filter(object):

    def __init__(self, field_type):
        self.field_type = field_type

    def validate_input(self):
        self.validated_value = self.field_type.deserialize_value()

    def bind(self, filter_field):
        """
        Bind the name of the filter - this is what appears to the API
        """
        self.filter_field = filter_field
        self.field_type.bind(self, self.filter_field, request.args)


class FilterSet(object):
    """
    FilterSet Base class

    For defining various kinds of filters
    """

    def __init__(self):
        self.filters = []
        for filter_name, filter_obj in self.__class__.__dict__.items():
            if isinstance(filter_obj, Filter):
                filter_obj.bind(filter_name)
                self.filters.append(filter_obj)

    def validate_inputs(self):
        for filter_obj in self.filters:
            filter_obj.validate_input()
