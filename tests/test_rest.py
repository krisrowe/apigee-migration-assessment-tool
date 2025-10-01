"""Test suite for rest."""
import json
import sys
import unittest
from unittest.mock import Mock, patch
from rest import (ApigeeError, EmptyResponse, JsonResponse, PlainResponse,  # noqa
                  RawResponse, RestClient)
sys.path.insert(0, '..')


class TestRestClient(unittest.TestCase):
    """Test class for RestClient."""

    def setUp(self):
        """Set up."""
        self.mock_session = Mock()
        self.patcher = patch('rest.requests.Session',
                             return_value=self.mock_session)
        self.mock_session_class = self.patcher.start()

    def tearDown(self):
        """Tear down."""
        self.patcher.stop()

    def test_init_valid_auth_type(self):
        """Test init valid auth type."""
        client = RestClient(auth_type='basic', token='test_token')
        self.assertEqual(client.auth_type, 'basic')
        self.assertEqual(client.base_headers['Authorization'],
                         'Basic test_token')

        client = RestClient(auth_type='oauth', token='test_token')
        self.assertEqual(client.auth_type, 'oauth')
        self.assertEqual(client.base_headers['Authorization'],
                         'Bearer test_token')

    def test_init_invalid_auth_type(self):
        """Test init invalid auth type."""
        with self.assertRaises(ValueError):
            RestClient(auth_type='invalid', token='test_token')

    def _prepare_mock_response(self, status_code, content,
                               content_type='application/json'):
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_response.text = json.dumps(
            content) if content_type == 'application/json' else content
        mock_response.content = bytes(mock_response.text,
                                      'utf-8') if isinstance(
            content, str) else content
        mock_response.headers = {'Content-Type': content_type}
        mock_response.request = Mock()
        mock_response.request.method = 'GET'
        mock_response.request.url = 'http://example.com'
        return mock_response

    def test_get_success(self):
        """Test get success."""
        mock_response = self._prepare_mock_response(200, {'key': 'value'})
        self.mock_session.get.return_value = mock_response

        client = RestClient(auth_type='basic', token='test')
        response = client.get('http://example.com')

        self.assertEqual(response, {'key': 'value'})
        self.mock_session.get.assert_called_once_with(
            'http://example.com', params=None,
            headers={'Authorization': 'Basic test'}
        )

    def test_post_success(self):
        """Test post success."""
        mock_response = self._prepare_mock_response(200,
                                                    {'status': 'created'})
        self.mock_session.post.return_value = mock_response

        client = RestClient(auth_type='basic', token='test')
        response = client.post('http://example.com', data={'name': 'test'})

        self.assertEqual(response, {'status': 'created'})
        self.mock_session.post.assert_called_once_with(
            'http://example.com', data='{"name": "test"}',
            headers={'Authorization': 'Basic test'}
        )

    def test_file_get_success(self):
        """Test file get success."""
        mock_response = self._prepare_mock_response(
            200, b'file_content', 'application/octet-stream')
        self.mock_session.get.return_value = mock_response

        client = RestClient(auth_type='basic', token='test')
        response = client.file_get('http://example.com/file')

        self.assertEqual(response, b'file_content')
        self.mock_session.get.assert_called_once()

    def test_file_post_success(self):
        """Test file post success."""
        mock_response = self._prepare_mock_response(200,
                                                    {'status': 'uploaded'})
        self.mock_session.post.return_value = mock_response

        client = RestClient(auth_type='basic', token='test')
        response = client.file_post(
                'http://example.com/upload',
                data={'field': 'value'},
                files={'file': b'content'}
                )

        self.assertEqual(response, {'status': 'uploaded'})
        self.mock_session.post.assert_called_once()

    def test_403_forbidden(self):
        """Test 403 forbidden."""
        mock_response = self._prepare_mock_response(403, 'Forbidden')
        self.mock_session.get.return_value = mock_response

        client = RestClient(auth_type='basic', token='test')
        response = client.get('http://example.com')

        self.assertEqual(response, 'Forbidden')

    def test_apigee_error(self):
        """Test apigee error."""
        error_content = {'errorCode': 'some.error',
                         'message': 'An error occurred'}
        mock_response = self._prepare_mock_response(400, error_content)
        self.mock_session.get.return_value = mock_response
        # Force _is_error to return True
        with patch('rest.Response._is_error', return_value=True):
            client = RestClient(auth_type='basic', token='test')
            with self.assertRaises(ApigeeError) as cm:
                client.get('http://example.com')

            self.assertEqual(cm.exception.status_code, 400)
            self.assertEqual(cm.exception.error_code, 'some.error')
            self.assertEqual(cm.exception.message, 'An error occurred')


class TestResponseClasses(unittest.TestCase):
    """Test class for ResponseClasses."""

    def test_json_response(self):
        """Test json response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"key": "value"}'
        response = JsonResponse(mock_response)
        self.assertEqual(response.content(), {"key": "value"})

    def test_plain_response(self):
        """Test plain response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = 'OK'
        response = PlainResponse(mock_response)
        self.assertEqual(response.content(), 'OK')

    def test_empty_response(self):
        """Test empty response."""
        response = EmptyResponse(204)
        self.assertEqual(response.content(), '')

    def test_raw_response(self):
        """Test raw response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'raw_data'
        response = RawResponse(mock_response)
        self.assertEqual(response.content(), b'raw_data')


if __name__ == '__main__':
    unittest.main()
