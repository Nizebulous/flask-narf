from flask import json
from flask.ext.narf.fields import URIField

from test_api import APITest, TEST_API


class ContentTypeTest(APITest):

    # TODO(Dom): Additional tests:
    #   1. Test field_name support for each Content-Type
    #   2. Test display_prompt support for each Content-Type

    def setUp(self):
        self.client = TEST_API.app.test_client()

    def get(self, path):
        return self.client.get(path, headers={'Accept': self.CONTENT_TYPE})


class TestJSON(ContentTypeTest):
    """
    Test Content-Type: JSON handler
    """
    CONTENT_TYPE = 'application/json'

    def verify_response_format(self, raw_data, fields):
        """
        Verify the response format for Content-Type: JSON
        """
        data = json.loads(raw_data)
        self.assertIsInstance(fields, dict)
        self.assertIsInstance(data, dict)
        self.assertIn('items', data)
        items = data.pop('items')
        self.assertIsInstance(items, list)
        for item in items:
            self.assertIsInstance(item, dict)
            for field, class_type in fields.items():
                self.assertIn(field, item)
                self.assertIsInstance(item[field], class_type)

    def test_json_default_endpoint_dict(self):
        """
        Test Content-Type: JSON on default endpoint returning a dict
        """
        response = self.get('/dict')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, '{"hello": "world"}')

    def test_json_default_endpoint_list(self):
        """
        Test Content-Type: JSON on default endpoint returning a list
        """
        response = self.get('/list')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, '[{"hello": "world"}]')

    def test_json_default_endpoint_obj(self):
        """
        Test Content-Type: JSON on default endpoint returning an object
        """
        response = self.get('/obj')
        self.assertEqual(response.status_code, 500)
        # TODO(Dom): Update with more details once better error handling has been introduced

    def test_json_fields_endpoint_dict(self):
        """
        Test Content-Type: JSON on an endpoint with each kind of supported field returning a dict
        """
        response = self.get('/dict/fields')
        self.assertEqual(response.status_code, 200)
        self.verify_response_format(response.data, {'field': basestring})

    def test_json_fields_endpoint_list(self):
        """
        Test Content-Type: JSON on an endpoint with each kind of supported field returning a list
        """
        response = self.get('/list/fields')
        self.assertEqual(response.status_code, 200)
        self.verify_response_format(response.data, {'field': basestring})

    def test_json_fields_endpoint_obj(self):
        """
        Test Content-Type: JSON on an endpoint with each kind of supported field returning an object
        """
        response = self.get('/obj/fields')
        self.assertEqual(response.status_code, 200)
        self.verify_response_format(response.data, {'field': basestring})


class TestCollectionPlusJSON(ContentTypeTest):
    """
    Test Content-Type: vnd.collection+json
    """
    CONTENT_TYPE = 'application/vnd.collection+json'

    # TODO(Dom): Additional tests:
    #   1. Endpoint with no pk field

    def verify_response_format(self, raw_data, fields):
        """
        Verify the response format for Content-Type: vnd.collection+json
        """
        # TODO(Dom): add more specifics on various field validation
        payload_data = json.loads(raw_data)
        self.assertIsInstance(fields, dict)
        self.assertIsInstance(payload_data, dict)
        self.assertIn('collection', payload_data)
        collection = payload_data['collection']
        self.assertIsInstance(collection, dict)
        self.assertIn('items', collection)
        version = collection.get('version')
        if version:
            self.assertIsInstance(version, basestring)
        items = collection['items']
        for item in items:
            self.assertIsInstance(item, dict)
            self.assertIn('href', item)
            self.assertIsInstance(item['href'], basestring)
            links = {}
            data = {}
            if 'links' in item:
                for link in item['links']:
                    self.assertIsInstance(link, dict)
                    links[link['rel']] = link
            if 'data' in item:
                for data_obj in item['data']:
                    self.assertIsInstance(data_obj, dict)
                    data[data_obj['name']] = data_obj
            for field, class_type in fields.items():
                if isinstance(field, URIField):
                    self.assertIn(field, links)
                else:
                    self.assertIn(field, data)

    def test_collection_default_endpoint_dict(self):
        """
        Test Content-Type: CollectionPlusJSON on default endpoint returning a dict
        """
        response = self.get('/dict')
        self.assertEqual(response.status_code, 500)
        # TODO(Dom): Update with more details once better error handling has been introduced

    def test_collection_default_endpoint_list(self):
        """
        Test Content-Type: CollectionPlusJSON on default endpoint returning a list
        """
        response = self.get('/list')
        self.assertEqual(response.status_code, 500)
        # TODO(Dom): Update with more details once better error handling has been introduced

    def test_collection_default_endpoint_obj(self):
        """
        Test Content-Type: CollectionPlusJSON on default endpoint returning an object
        """
        response = self.get('/obj')
        self.assertEqual(response.status_code, 500)
        # TODO(Dom): Update with more details once better error handling has been introduced

    def test_collection_fields_endpoint_dict(self):
        """
        Test Content-Type: CollectionPlusJSON on an endpoint with each kind of supported field returning a dict
        """
        response = self.get('/dict/fields')
        self.assertEqual(response.status_code, 200)
        self.verify_response_format(response.data, {'field': basestring})

    def test_collection_fields_endpoint_list(self):
        """
        Test Content-Type: CollectionPlusJSON on an endpoint with each kind of supported field returning a list
        """
        response = self.get('/list/fields')
        self.assertEqual(response.status_code, 200)
        self.verify_response_format(response.data, {'field': basestring})

    def test_collection_fields_endpoint_obj(self):
        """
        Test Content-Type: CollectionPlusJSON on an endpoint with each kind of supported field returning an object
        """
        response = self.get('/obj/fields')
        self.assertEqual(response.status_code, 200)
        self.verify_response_format(response.data, {'field': basestring})
