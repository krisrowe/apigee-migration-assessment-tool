
"""
Tests for the exporter module.
"""
import unittest
from unittest.mock import MagicMock, patch, mock_open

from exporter import ApigeeExporter


class TestApigeeExporter(unittest.TestCase):
    """
    Test cases for the ApigeeExporter class.
    """

    def setUp(self):
        """
        Set up the test case.
        """
        self.baseurl = "https://api.enterprise.apigee.com/v1"
        self.org = "test_org"
        self.token = "test_token"
        self.auth_type = "oauth"
        self.ssl_verify = True
        with patch('exporter.ApigeeClassic'):
            self.exporter = ApigeeExporter(self.baseurl, self.org, self.token,
                                           self.auth_type, self.ssl_verify)
            self.exporter.apigee = MagicMock()

    def test_export_env(self):
        """
        Test the export_env method.
        """
        self.exporter.apigee.list_environments.return_value = ["test", "prod"]
        self.exporter.export_env()
        self.assertIn("test", self.exporter.export_data['envConfig'])
        self.assertIn("prod", self.exporter.export_data['envConfig'])

    def test_export_vhosts_edge(self):
        """
        Test the export_vhosts method for Edge.
        """
        self.exporter.apigee_type = 'edge'
        self.exporter.export_data['envConfig'] = {"test": {}}
        self.exporter.apigee.list_env_vhosts.return_value = ["default",
                                                             "secure"]
        self.exporter.apigee.get_env_vhost.return_value = {"name": "default"}
        self.exporter.export_vhosts()
        self.assertIn("vhosts", self.exporter.export_data['envConfig']['test'])
        self.assertEqual(
            len(self.exporter.export_data['envConfig']['test']['vhosts']), 2)

    def test_export_vhosts_x(self):
        """
        Test the export_vhosts method for X/Hybrid.
        """
        self.exporter.apigee_type = 'x'
        self.exporter.apigee.list_env_groups.return_value = {"default": {}}
        self.exporter.export_vhosts()
        self.assertIn("envgroups", self.exporter.export_data['orgConfig'])

    @patch('exporter.create_dir')
    @patch('exporter.write_file')
    def test_export_env_objects_resourcefiles(self, mock_write_file,
                                              mock_create_dir):
        """
        Test the export_env_objects method for resourcefiles.
        """
        self.exporter.export_data['envConfig'] = {"test":
                                                  {"resourcefiles": {}}}
        self.exporter.apigee.list_env_objects.return_value = {
            'resourceFile': [{'name': 'test.js', 'type': 'jsc'}]}
        self.exporter.apigee.get_env_object.return_value = b"content"
        self.exporter.export_env_objects(['resourcefiles'], 'export_dir')
        mock_create_dir.assert_called_with('export_dir/resourceFiles/jsc')
        mock_write_file.assert_called_with(
            'export_dir/resourceFiles/jsc/test.js', b"content")

    def test_export_org_objects(self):
        """
        Test the export_org_objects method.
        """
        self.exporter.apigee.list_org_objects.return_value = ["dev1"]
        self.exporter.apigee.get_org_object.return_value = {
            "email": "a@a.com"}
        self.exporter.export_org_objects(['developers'])
        self.assertIn("developers", self.exporter.export_data['orgConfig'])
        self.assertIn("dev1",
                      self.exporter.export_data['orgConfig']['developers'])

    def test_export_api_metadata(self):
        """
        Test the export_api_metadata method.
        """
        self.exporter.export_data['envConfig'] = {"test": {}}
        self.exporter.export_data['orgConfig'] = {}
        self.exporter.apigee.list_org_objects.return_value = ["api1"]
        self.exporter.apigee.list_api_revisions.return_value = ["1", "2"]
        self.exporter.apigee.api_env_mapping.return_value = {
            "environment": [{"name": "test", "revision": [{"name": "1"}]}]}
        self.exporter.export_api_metadata(['apis'])
        self.assertIn("apis", self.exporter.export_data['orgConfig'])
        self.assertIn("api1", self.exporter.export_data['orgConfig']['apis'])
        self.assertIn("apis", self.exporter.export_data['envConfig']['test'])
        self.assertIn(
                        "api1",
                        self.exporter.export_data['envConfig']['test']['apis']
                        )

    @patch('exporter.run_parallel')
    def test_export_api_proxy_bundles(self, mock_run_parallel):
        """
        Test the export_api_proxy_bundles method.
        """
        self.exporter.export_data['orgConfig'] = {"apis": {"api1": {}}}
        self.exporter.export_api_proxy_bundles('export_dir', ['apis'])
        mock_run_parallel.assert_called_once()

    @patch('os.path.isdir')
    @patch('os.listdir')
    @patch('builtins.open', new_callable=mock_open,
           read_data='{"key": "value"}')
    # pylint: disable=unused-argument
    def test_read_export_state(self, mock_open_file, mock_listdir, mock_isdir):
        """
        Test the read_export_state method.
        """
        mock_isdir.side_effect = [True, False]
        mock_listdir.side_effect = [['orgConfig'], ['file.json']]
        data = self.exporter.read_export_state('folder_path')
        self.assertIn('orgConfig', data)
        self.assertIn('file', data['orgConfig'])

    def test_get_dependencies_data(self):
        """
        Test the get_dependencies_data method.
        """
        self.exporter.apigee.list_environments.return_value = ["test"]
        self.exporter.apigee.list_env_objects.return_value = ["ref1"]
        self.exporter.apigee.get_env_object.return_value = {"name": "ref1"}
        data = self.exporter.get_dependencies_data(['references'])
        self.assertIn('references', data)
        self.assertIn('test', data['references'])
        self.assertIn('ref1', data['references']['test'])


if __name__ == '__main__':
    unittest.main()
