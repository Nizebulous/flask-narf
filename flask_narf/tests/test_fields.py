from mock import patch
from unittest import TestCase

from flask.ext.narf.fields import Field, StringField, URIField, RelatedURIField, FieldRef


class TestField(TestCase):

    def test_field_default(self):
        """
        Test a Field with default configuration
        """
        field = Field()
        value = 'field_name'
        field.bind(self, 'field_name', {'field_name': value})
        self.assertEqual(value, field.serialize_value())
        self.assertFalse(field.pk)
        self.assertIsNone(field.display_prompt)

    def test_field_source_override(self):
        """
        Test a Field with source overriden
        """
        field = Field(source='source')
        value = 'field_name'
        field.bind(self, 'field_name', {'source': value})
        self.assertEqual(value, field.serialize_value())

    def test_field_pk_override(self):
        """
        Test a Field with pk overriden
        """
        field = Field(pk=True)
        self.assertTrue(field.pk)

    def test_field_display_prompt_override(self):
        """
        Test a Field with pk overriden
        """
        value = 'display'
        field = Field(display_prompt=value)
        self.assertEqual(value, field.display_prompt)


class TestStringField(TestCase):

    def test_field_default(self):
        """
        Test a StringField with default configuration
        """
        field = StringField()
        value = 'field_name'
        field.bind(self, 'field_name', {'field_name': value})
        self.assertIsInstance(field.serialize_value(), unicode)
        self.assertEqual(value, field.serialize_value())
        self.assertFalse(field.pk)
        self.assertIsNone(field.display_prompt)

    def test_field_source_override(self):
        """
        Test a StringField with source overriden
        """
        field = StringField(source='source')
        value = 'field_name'
        field.bind(self, 'field_name', {'source': value})
        self.assertIsInstance(field.serialize_value(), unicode)
        self.assertEqual(value, field.serialize_value())

    def test_field_pk_override(self):
        """
        Test a StringField with pk overriden
        """
        field = StringField(pk=True)
        self.assertTrue(field.pk)

    def test_field_display_prompt_override(self):
        """
        Test a StringField with pk overriden
        """
        value = 'display'
        field = StringField(display_prompt=value)
        self.assertEqual(value, field.display_prompt)


class TestURIField(TestCase):

    def test_field_default(self):
        """
        Test a URIField with default configuration
        """
        field = URIField()
        value = 'field_name'
        field.bind(self, 'field_name', {'field_name': value})
        self.assertIsInstance(field.serialize_value(), unicode)
        self.assertEqual(value, field.serialize_value())
        self.assertFalse(field.pk)
        self.assertIsNone(field.display_prompt)
        self.assertIsNone(field.relation)

    def test_field_source_override(self):
        """
        Test a URIField with source overriden
        """
        field = URIField(source='source')
        value = 'field_name'
        field.bind(self, 'field_name', {'source': value})
        self.assertIsInstance(field.serialize_value(), unicode)
        self.assertEqual(value, field.serialize_value())

    def test_field_pk_override(self):
        """
        Test a URIField with pk overriden
        """
        field = URIField(pk=True)
        self.assertTrue(field.pk)

    def test_field_display_prompt_override(self):
        """
        Test a URIField with pk overriden
        """
        value = 'display'
        field = URIField(display_prompt=value)
        self.assertEqual(value, field.display_prompt)

    def test_field_relation_override(self):
        """
        Test a URIField with relation overriden
        """
        value = 'relation'
        field = URIField(relation=value)
        self.assertEqual(value, field.relation)


class TestRelatedURIField(TestCase):

    source = Field()

    def setUp(self):
        self.source.bind(self, 'source', {'source': 'source_value'})

    @patch('flask.ext.narf.fields.url_for')
    @patch('flask.ext.narf.fields.request')
    def test_field_default(self, request, url_for):
        """
        Test a RelatedURIField with default configuration
        """
        request.url_root = 'http://api.narf.com/'
        url_for.return_value = '/api/v1/endpoint'
        field = RelatedURIField('endpoint')
        value = 'http://api.narf.com/api/v1/endpoint'
        field.bind(self, 'field_name', {'source': 'relation'})
        self.assertIsInstance(field.serialize_value(), unicode)
        self.assertEqual(value, field.serialize_value())
        self.assertFalse(field.pk)
        self.assertIsNone(field.display_prompt)
        self.assertIsNone(field.relation)

    @patch('flask.ext.narf.fields.url_for')
    @patch('flask.ext.narf.fields.request')
    def test_field_filters_override(self, request, url_for):
        """
        Test a RelatedURIField with filters overriden
        """
        request.url_root = 'http://api.narf.com/'
        url_for.return_value = '/api/v1/endpoint'
        field = RelatedURIField('endpoint', filters={'filter': 'filter'})
        value = 'http://api.narf.com/api/v1/endpoint?filter=filter'
        field.bind(self, 'field_name', {'source': 'relation'})
        self.assertIsInstance(field.serialize_value(), unicode)
        self.assertEqual(value, field.serialize_value())

    @patch('flask.ext.narf.fields.url_for')
    @patch('flask.ext.narf.fields.request')
    def test_field_filters_override_with_field_ref(self, request, url_for):
        """
        Test a RelatedURIField with filters overriden and a field reference
        """
        request.url_root = 'http://api.narf.com/'
        url_for.return_value = '/api/v1/endpoint'
        field = RelatedURIField('endpoint', filters={'filter': FieldRef('source')})
        value = 'http://api.narf.com/api/v1/endpoint?filter=source_value'
        field.bind(self, 'field_name', {'filter': 'filter'})
        self.assertIsInstance(field.serialize_value(), unicode)
        self.assertEqual(value, field.serialize_value())

    def test_field_pk_override(self):
        """
        Test a RelatedURIField with pk overriden
        """
        field = RelatedURIField('endpoint', pk=True)
        self.assertTrue(field.pk)

    def test_field_display_prompt_override(self):
        """
        Test a RelatedURIField with pk overriden
        """
        value = 'display'
        field = RelatedURIField('endpoint', display_prompt=value)
        self.assertEqual(value, field.display_prompt)

    def test_field_relation_override(self):
        """
        Test a RelatedURIField with relation overriden
        """
        value = 'relation'
        field = RelatedURIField('endpoint', relation=value)
        self.assertEqual(value, field.relation)
