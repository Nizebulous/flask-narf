from flask import request


class Field(object):
    """
    Base Field Serializer/deserializer

    Used for defining fields on Serializers and Deserializers

    The Field object has 2 purposes:
        1. Serialize/Deserialize field values based on type
        2. Store information about the field that would be useful for a ContentType
    """

    class UnsetValue(object):
        pass

    UNSET = UnsetValue()

    def __init__(self, source=None, pk=False, display_prompt=None):
        self._source = source
        self.pk = pk
        self.display_prompt = display_prompt
        self.field_name = None
        self.raw_value = self.UNSET

    def serialize_value(self):
        return self.raw_value

    def deserialize_value(self):
        return self.raw_value

    def bind(self, parent, field_name, raw_data):
        self.parent = parent
        self.field_name = field_name
        self.raw_data = raw_data
        if isinstance(raw_data, dict):
            self.raw_value = raw_data.get(self.source, None)
        else:
            self.raw_value = getattr(raw_data, self.source, None)

    @property
    def source(self):
        return self._source if self._source is not None else self.field_name


class StringField(Field):

    def serialize_value(self):
        return str(self.raw_value)

    def deserialize_value(self):
        return str(self.raw_value) if self.raw_value is not None else None


class FieldRef(Field):

    def serialize_value(self):
        return getattr(self.parent, self.source).serialize_value()


class URIField(Field):
    """
    URI Field

    For validating and handling URI's
    """

    def __init__(self, relation=None, **kwargs):
        self.relation = relation
        super(URIField, self).__init__(**kwargs)


class RelatedURIField(URIField):
    def __init__(self, related_endpoint=None, filters=None, **kwargs):
        self.related_endpoint = related_endpoint.lstrip('/')
        self.filters = filters
        super(RelatedURIField, self).__init__(**kwargs)

    def serialize_value(self):
        query_string = '?' if self.filters else ''
        for param, value in self.filters.items():
            if isinstance(value, FieldRef):
                value.bind(self.parent, param, self.raw_data)
                value = value.serialize_value()
            query_string += '%s=%s' % (param, value)
        return request.url_root + self.related_endpoint + query_string
