from re import sub
from traceback import format_tb

from flask import request, Response, json

from flask.ext.narf.fields import URIField


class ContentType(object):
    """
    ContentType Base class

    For defining a Content-Type. Manages the data format.
    """

    CONTENT_TYPE = None

    def __init__(self, endpoint):
        self.endpoint = endpoint

    def serialize(self, obj):
        """
        Serialize the result of the view function into the correct format for this Content-Type
        """
        if not isinstance(obj, list):
            item_list = [obj]
        else:
            item_list = obj
        items = self.serialize_item_list(item_list)
        return self.serialize_response(items)

    def serialize_item(self, item):
        """
        Serialize a single item
        """
        serializer = self.endpoint.Serializer(raw_data=item)
        return {field.field_name: field.serialize_value() for field in serializer.fields}

    def serialize_item_list(self, item_list):
        """
        Serialize a list of items according to the Content-Type format
        """
        items = [self.serialize_item(item) for item in item_list]
        return items

    def make_response(self, return_format):
        """
        Make a response with Content-Type: application/collection+json
        """
        return Response(return_format, mimetype=self.CONTENT_TYPE)


class JSON(ContentType):
    """
    Content-Type: application/json
    """

    CONTENT_TYPE = 'application/json'

    def serialize_response(self, items):
        return json.dumps({'items': items})

    def make_error_response(self, exc_type, exc_value, exc_traceback):
        return Response(
            json.dumps(
                {
                    'error': str(exc_type),
                    'message': str(exc_value),
                    'stacktrace': format_tb(exc_traceback)
                }
            ),
            status=500
        )


class CollectionPlusJSON(ContentType):
    """
    Content-Type: application/collection+json
    """

    CONTENT_TYPE = 'application/vnd.collection+json'

    def serialize_item(self, item):
        """
        Serialize a specific item according to the Content-Type format
        """
        data = []
        links = []
        serializer = self.endpoint.Serializer(item)
        for field in serializer.fields:
            value = field.serialize_value()
            prompt = field.display_prompt
            if field.pk:
                pk_field = field
            if isinstance(field, URIField):
                relation = field.relation or field.field_name
                field_data = {'href': value, 'rel': relation}
                if prompt:
                    field_data['prompt'] = prompt
                links.append(field_data)
            else:
                field_data = {'name': field.field_name, 'value': value}
                if prompt:
                    field_data['prompt'] = prompt
                data.append(field_data)
        obj = {
            'href': request.url_root + sub(
                r'\<.+?\>',
                str(pk_field.serialize_value()),
                self.endpoint.path.lstrip('/')
            )
        }
        if data:
            obj['data'] = data
        if links:
            obj['links'] = links
        return obj

    def serialize_response(self, items):
        collection = {'href': request.url}
        if items:
            collection['items'] = items
        return json.dumps({'collection': collection})

    def make_error_response(self, exc_type, exc_value, exc_traceback):
        return Response(
            json.dumps(
                {
                    'collection': {
                        'title': str(exc_type),
                        'code': str(exc_type),
                        'message': str(exc_value),
                        'stacktrace': format_tb(exc_traceback)
                    }
                }
            ),
            status=500
        )
