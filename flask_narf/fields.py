from urllib import urlencode

from flask import request, url_for


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
        # TODO(Dom): add support for non-required fields

    def serialize_value(self):
        return self.raw_value

    def deserialize_value(self):
        return self.raw_value

    def _populate_raw_value(self):
        if isinstance(self.raw_data, dict):
            self.raw_value = self.raw_data[self.source]
        else:
            self.raw_value = getattr(self.raw_data, self.source)

    def bind(self, parent, field_name, raw_data):
        self.parent = parent
        self.field_name = field_name
        self.raw_data = raw_data
        self._populate_raw_value()

    @property
    def source(self):
        return self._source if self._source is not None else self.field_name


class StringField(Field):

    def serialize_value(self):
        return unicode(self.raw_value)

    def deserialize_value(self):
        return unicode(self.raw_value) if self.raw_value is not None else None


class FieldRef(Field):

    def _populate_raw_value(self):
        """
        Override to avoid looking for the raw_value since we generate it
        """
        return

    def serialize_value(self):
        return getattr(self.parent, self.source).serialize_value()


class URIField(StringField):
    """
    URI Field

    For validating and handling URI's
    """

    def __init__(self, relation=None, **kwargs):
        self.relation = relation
        super(URIField, self).__init__(**kwargs)


class RelatedURIField(URIField):

    def __init__(self, related_endpoint, filters=None, **kwargs):
        self.related_endpoint = related_endpoint.lstrip('/')
        self.filters = filters or {}
        super(RelatedURIField, self).__init__(**kwargs)

    def _populate_raw_value(self):
        """
        Override to avoid looking for the raw_value since we generate it
        """
        return

    def serialize_value(self):
        params = {}
        url_root = request.url_root.rstrip('/')
        for param, value in self.filters.items():
            if isinstance(value, FieldRef):
                value.bind(self.parent, param, self.raw_data)
                params[param] = value.serialize_value()
            else:
                params[param] = value
        param_string = '?{0}'.format(urlencode(params)) if params else ''
        return u'{0}{1}{2}'.format(url_root, url_for(self.related_endpoint), param_string)
