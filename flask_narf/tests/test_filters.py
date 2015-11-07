from mock import patch
from unittest import TestCase

from flask.ext.narf.fields import Field, StringField
from flask.ext.narf.filters import Filter, FilterSet


class TestFilter(TestCase):

    @patch('flask.ext.narf.filters.request')
    def test_filter(self, request):
        """
        Test a Filter
        """
        request.args = {'field': 'input'}
        field = Filter(Field())
        field.bind('field')
        field.validate_input()
        self.assertEqual(field.validated_value, 'input')


class TestFilterSet(TestCase):

    @patch('flask.ext.narf.filters.request')
    def test_filter_set(self, request):
        """
        Test a FilterSet
        """
        request.args = {'field': 'input', 'string_field': 'string_input'}

        class MyFilterSet(FilterSet):
            field = Filter(Field())
            string_field = Filter(StringField())

        filter_set = MyFilterSet()
        filter_set.validate_inputs()
        self.assertEqual(filter_set.field.validated_value, 'input')
        self.assertEqual(filter_set.string_field.validated_value, 'string_input')

    @patch('flask.ext.narf.filters.request')
    def test_filter_set_no_fields_provided(self, request):
        """
        Test a FilterSet without providing anything in args
        """
        request.args = {}

        class MyFilterSet(FilterSet):
            field = Filter(Field())
            string_field = Filter(StringField())

        filter_set = MyFilterSet()
        filter_set.validate_inputs()
        self.assertIsNone(filter_set.field.validated_value)
        self.assertIsNone(filter_set.string_field.validated_value)
