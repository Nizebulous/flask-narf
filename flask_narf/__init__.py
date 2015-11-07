from re import sub
from sys import exc_info

from flask import request

from flask.ext.narf.filters import FilterSet
from flask.ext.narf.serializers import Serializer
from flask.ext.narf.deserializers import Deserializer
from flask.ext.narf.content_types import ContentType, JSON, CollectionPlusJSON


class Endpoint(object):
    """
    Endpoint object

    For tracking serializer, deserializer, filterset and the various content-types for a given
    endpoint.
    Also contains setup and teardown logic for all endpoints.
    """

    def __init__(self):
        """
        Initialize with default endpoint behavior.
        """
        self.FilterSet = None
        self.Deserializer = None
        self.content_type = None
        self.Serializer = None
        self.content_type_map = {}
        self.filter_set = None
        self.content_type = None

    def bind(self, api, path, func, decorated):
        """
        Bind this endpoint to the API at a specific path with a specific function
        """
        self.api = api
        self.path = path
        self.func = func
        self.decorated = decorated
        self.base_path = sub(r'<.+?>', '', path)
        if api.app:
            self.init_app(api.app)

    def init_app(self, app):
        """
        Initialize this endpoint with the Flask app when it's available
        """
        app.add_url_rule(self.path, self.func.__name__, view_func=self.decorated)
        # Generate the content_type_map with this priority:
        #   1. endpoint content-type overrides
        #   2. global content-type overrides
        #   3. default content-types
        for content_type, content_type_class in app.config['DEFAULT_CONTENT_TYPE_MAP'].items():
            self.content_type_map.setdefault(content_type, content_type_class)

    def setup_request(self):
        """
        Setup the request for this endpoint
        """
        best = request.accept_mimetypes.best_match(self.content_type_map.keys())
        self.content_type = self.content_type_map[best](self)
        if self.FilterSet:
            self.filter_set = self.FilterSet()
            self.filter_set.validate_inputs()

    def teardown_request(self):
        """
        Teardown the request for this endpoint (cleanup)
        """
        self.content_type = None
        self.filter_set = None


class NARF():
    """
    Not Another Rest Framework
    """

    def __init__(self, app=None):
        self.app = app
        self.endpoints = {}
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """
        Initialize the NARF extension with this app
        """
        self.app = app
        # setup the default content-types taking into account global overrides
        app.config.setdefault(
            'DEFAULT_CONTENT_TYPE_MAP',
            {
                'text/html': JSON,
                JSON.CONTENT_TYPE: JSON,
                CollectionPlusJSON.CONTENT_TYPE: CollectionPlusJSON
            }
        )
        # Use the newstyle teardown_appcontext if it's available,
        # otherwise fall back to the request context
        if hasattr(app, 'teardown_appcontext'):
            app.teardown_appcontext(self.teardown)
        else:
            app.teardown_request(self.teardown)
        # initialize all the endpoints
        for endpoint in self.endpoints.values():
            endpoint.init_app(app)

    def teardown(self, exception):
        """
        Cleanup app context
        """
        pass

    def get_endpoint(self, name):
        endpoint = self.endpoints.get(name)
        if endpoint is None:
            endpoint = Endpoint()
            self.endpoints[name] = endpoint
        return endpoint

    def register_filterset(self, target):
        def decorator(func):
            endpoint = self.get_endpoint(func.__name__)
            endpoint.FilterSet = target
            return func
        return decorator

    def register_deserializer(self, target):
        def decorator(func):
            endpoint = self.get_endpoint(func.__name__)
            endpoint.Deserializer = target
            return func
        return decorator

    def register_serializer(self, target):
        def decorator(func):
            endpoint = self.get_endpoint(func.__name__)
            endpoint.Serializer = target
            return func
        return decorator

    def register_content_type(self, target):
        def decorator(func):
            endpoint = self.get_endpoint(func.__name__)
            endpoint.content_type_map[target.CONTENT_TYPE] = target
            return func
        return decorator

    def register(self, target):
        """
        Register endpoint component
        """
        if issubclass(target, FilterSet):
            return self.register_filterset(target)
        if issubclass(target, Deserializer):
            return self.register_deserializer(target)
        if issubclass(target, Serializer):
            return self.register_serializer(target)
        if issubclass(target, ContentType):
            return self.register_content_type(target)

    def endpoint(self, path):
        """
        Define an endpoint in the API
        """
        # decorate the endpoint
        def decorator(func):
            def decorated(*args, **kwargs):
                try:
                    endpoint.setup_request()
                    if endpoint.filter_set:
                        kwargs['filterset'] = endpoint.filter_set
                    returned_object = func(*args, **kwargs)
                    serialized_data = endpoint.content_type.serialize(returned_object)
                    response = endpoint.content_type.make_response(serialized_data)
                except Exception:
                    exc_type, exc_value, exc_traceback = exc_info()
                    response = endpoint.content_type.make_error_response(
                        exc_type, exc_value, exc_traceback
                    )
                endpoint.teardown_request()
                return response

            # setup the endpoint
            endpoint = self.get_endpoint(func.__name__)
            endpoint.bind(self, path, func, decorated)

            return func

        return decorator

    def resource(self, cls):
        """
        Define an entire resource
        """
        pass
