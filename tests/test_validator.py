"""
Tests for the validator module.
"""
import unittest
from unittest.mock import MagicMock, patch
from validator import ApigeeValidator


class TestApigeeValidator(unittest.TestCase):
    """
    Test cases for the ApigeeValidator class.
    """

    def setUp(self):
        """
        Set up the test case.
        """
        self.mock_apigee_new_gen = MagicMock()
        self.validator = ApigeeValidator(
            baseurl="https://mock.baseurl",
            project_id="mock_project",
            token="mock_token",
            env_type="hybrid",
            target_export_data={},
            target_compare=False,
            skip_target_validation=False,
            ssl_verify=True
        )
        self.validator.xorhybrid = self.mock_apigee_new_gen

    def test_validate_org_resource(self):
        """
        Test the validate_org_resource method.
        """
        resources = {"developers": {"dev1": {"name": "dev1"}}}
        result = self.validator.validate_org_resource("developers", resources)
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0]["importable"])
        self.assertEqual(result[0]["imported"], "UNKNOWN")

    def test_validate_kvms(self):
        """
        Test the validate_kvms method.
        """
        kvms = {"kvm1": {"name": "kvm1"}}
        result = self.validator.validate_kvms("test_env", kvms)
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0]["importable"])
        self.assertEqual(result[0]["imported"], "UNKNOWN")

    @patch('validator.list_dir')
    @patch('zipfile.ZipFile')
    # pylint: disable=unused-argument
    def test_validate_proxy_bundles(self, mock_zipfile, mock_list_dir):
        """
        Test the validate_proxy_bundles method.
        """
        self.validator.skip_target_validation = True
        export_objects = ['api1']
        validation = self.validator.validate_proxy_bundles(
            export_objects,
            '/tmp',
            '/tmp',
            'apis'
            )
        self.assertEqual(len(validation['apis']), 1)
        self.assertEqual(validation['apis'][0]['name'], 'api1')
        self.assertFalse(validation['apis'][0]['importable'])

    def test_validate_env_flowhooks(self):
        """
        Test the validate_env_flowhooks method.
        """
        flowhooks = {"fh1": {"name": "fh1", "sharedFlow": "sf1"}}
        self.mock_apigee_new_gen.get_env_object.return_value = {
            "deployments": []}
        result = self.validator.validate_env_flowhooks("test_env", flowhooks)
        self.assertEqual(len(result), 1)
        self.assertFalse(result[0]["importable"])
        self.assertEqual(result[0]["imported"], "UNKNOWN")


if __name__ == '__main__':
    unittest.main()
