from unittest import TestCase

from flask import Flask
from flask.ext.narf import NARF, Endpoint
from flask.ext.narf.fields import Field, StringField, URIField, RelatedURIField
from flask.ext.narf.filters import FilterSet
from flask.ext.narf.serializers import Serializer
from flask.ext.narf.deserializers import Deserializer
from flask.ext.narf.content_types import ContentType


class APITest(TestCase):
    """
    Base class for testing the API extension
    """

    def setUp(self):
        app = Flask(__name__)
        self.api = NARF(app)


class EndpointDeclaration(APITest):

    def verify_endpoint_declaration(
        self,
        endpoint,
        Serializer=None,
        Deserializer=None,
        FilterSet=None,
        content_types=None
    ):
        content_types = content_types or []
        inputs = {
            'Serializer': Serializer,
            'Deserializer': Deserializer,
            'FilterSet': FilterSet,
        }
        for field, value in inputs.items():
            if value is None:
                self.assertIsNone(getattr(endpoint, field))
            else:
                self.assertEqual(getattr(endpoint, field), value)

        content_type_map = self.api.app.config['DEFAULT_CONTENT_TYPE_MAP'].copy()
        for content_type in content_types:
            content_type_map[content_type.CONTENT_TYPE] = content_type
        self.assertDictEqual(content_type_map, endpoint.content_type_map)

    def test_default_endpoint(self):
        """
        Test endpoint creation with the default settings
        """

        @self.api.endpoint('/')
        def home():
            return {'hello': 'world'}

        # We should have 1 endpoint defined
        self.assertEqual(len(self.api.endpoints), 1)

        # Verify home_dict configuration
        self.assertIn('home', self.api.endpoints)
        home_endpoint = self.api.endpoints['home']
        self.assertIsInstance(home_endpoint, Endpoint)
        self.verify_endpoint_declaration(home_endpoint)

    def test_endpoint_with_serializer(self):
        """
        Test endpoint creation with a specified Serializer
        """

        class TestSerializer(Serializer):
            pass

        @self.api.register(TestSerializer)
        @self.api.endpoint('/')
        def home():
            return {'hello': 'world'}

        # We should have 1 endpoint defined
        self.assertEqual(len(self.api.endpoints), 1)

        # Verify home_dict configuration
        self.assertIn('home', self.api.endpoints)
        home_endpoint = self.api.endpoints['home']
        self.assertIsInstance(home_endpoint, Endpoint)
        self.verify_endpoint_declaration(home_endpoint, Serializer=TestSerializer)

    def test_endpoint_with_deserializer(self):
        """
        Test endpoint creation with a specified Deserializer
        """

        class TestDeserializer(Deserializer):
            pass

        @self.api.register(TestDeserializer)
        @self.api.endpoint('/')
        def home():
            return {'hello': 'world'}

        # We should have 1 endpoint defined
        self.assertEqual(len(self.api.endpoints), 1)

        # Verify home_dict configuration
        self.assertIn('home', self.api.endpoints)
        home_endpoint = self.api.endpoints['home']
        self.assertIsInstance(home_endpoint, Endpoint)
        self.verify_endpoint_declaration(home_endpoint, Deserializer=TestDeserializer)

    def test_endpoint_with_filterset(self):
        """
        Test endpoint creation with a specified FilterSet
        """

        class TestFilterSet(FilterSet):
            pass

        @self.api.register(TestFilterSet)
        @self.api.endpoint('/')
        def home():
            return {'hello': 'world'}

        # We should have 1 endpoint defined
        self.assertEqual(len(self.api.endpoints), 1)

        # Verify home_dict configuration
        self.assertIn('home', self.api.endpoints)
        home_endpoint = self.api.endpoints['home']
        self.assertIsInstance(home_endpoint, Endpoint)
        self.verify_endpoint_declaration(home_endpoint, FilterSet=TestFilterSet)

    def test_endpoint_with_content_type(self):
        """
        Test endpoint creation ADDING an unsupported Content-Type
        """

        class TestContentType(ContentType):
            CONTENT_TYPE = 'application/test'

        @self.api.register(TestContentType)
        @self.api.endpoint('/')
        def home():
            return {'hello': 'world'}

        # We should have 1 endpoint defined
        self.assertEqual(len(self.api.endpoints), 1)

        # Verify home_dict configuration
        self.assertIn('home', self.api.endpoints)
        home_endpoint = self.api.endpoints['home']
        self.assertIsInstance(home_endpoint, Endpoint)
        self.verify_endpoint_declaration(home_endpoint, content_types=[TestContentType])

    def test_endpoint_override_content_type(self):
        """
        Test endpoint creation OVERRIDING an existing Content-Type
        """

        class TestContentType(ContentType):
            CONTENT_TYPE = 'application/json'

        @self.api.register(TestContentType)
        @self.api.endpoint('/')
        def home():
            return {'hello': 'world'}

        # We should have 1 endpoint defined
        self.assertEqual(len(self.api.endpoints), 1)

        # Verify home_dict configuration
        self.assertIn('home', self.api.endpoints)
        home_endpoint = self.api.endpoints['home']
        self.assertIsInstance(home_endpoint, Endpoint)
        self.verify_endpoint_declaration(home_endpoint, content_types=[TestContentType])

    def test_with_app_not_inited(self):
        """
        Test endpoint creation with an app that hasn't been initialized yet
        """
        api = NARF()

        @api.endpoint('/')
        def home():
            return {'hello': 'world'}

        app = Flask(__name__)
        api.init_app(app)

        # We should have 1 endpoint defined
        self.assertEqual(len(api.endpoints), 1)

        # Verify home configuration
        self.assertIn('home', api.endpoints)
        home_endpoint = api.endpoints['home']
        self.assertIsInstance(home_endpoint, Endpoint)
        self.verify_endpoint_declaration(home_endpoint)

    def test_with_app_inited_before(self):
        """
        Test endpoint creation with an app that has endpoints added before and after initialization
        """
        api = NARF()

        @api.endpoint('/')
        def home():
            return {'hello': 'world'}

        app = Flask(__name__)
        api.init_app(app)

        @api.endpoint('/after')
        def after():
            return {'after': 'world'}

        # We should have 1 endpoint defined
        self.assertEqual(len(api.endpoints), 2)

        # Verify home configuration
        self.assertIn('home', api.endpoints)
        home_endpoint = api.endpoints['home']
        self.assertIsInstance(home_endpoint, Endpoint)
        self.verify_endpoint_declaration(home_endpoint)

        # Verify after configuration
        self.assertIn('after', api.endpoints)
        after_endpoint = api.endpoints['after']
        self.assertIsInstance(after_endpoint, Endpoint)
        self.verify_endpoint_declaration(after_endpoint)


class TestObject(object):
    pass


app = Flask(__name__)
TEST_API = NARF(app)


@TEST_API.endpoint('/dict')
def home_dict():
    return {'hello': 'world'}


@TEST_API.endpoint('/list')
def home_list():
    return [{'hello': 'world'}]


@TEST_API.endpoint('/obj')
def home_obj():
    obj = TestObject()
    obj.hello = 'world'
    return obj


class SupportedFieldsSerializer(Serializer):
    field = Field(pk=True)
    string = StringField()
    uri_field = URIField()
    related_uri_field = RelatedURIField('home_obj')


@TEST_API.register(SupportedFieldsSerializer)
@TEST_API.endpoint('/dict/fields')
def dict_fields():
    return {'field': 'field', 'string': 'string', 'uri_field': 'http://api.narf.com/'}


@TEST_API.register(SupportedFieldsSerializer)
@TEST_API.endpoint('/list/fields')
def list_fields():
    return [{'field': 'field', 'string': 'string', 'uri_field': 'http://api.narf.com/'}]


@TEST_API.register(SupportedFieldsSerializer)
@TEST_API.endpoint('/obj/fields')
def obj_fields():
    obj = TestObject()
    obj.field = 'field'
    obj.string = 'string'
    obj.uri_field = 'http://api.narf.com/'
    return [obj]
