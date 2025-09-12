
"""
Tests for the main module.
"""
import unittest
from unittest.mock import patch, MagicMock

from main import main


class TestMain(unittest.TestCase):
    """
    Test cases for the main function.
    """

    @patch('main.argparse.ArgumentParser')
    @patch('main.parse_config')
    @patch('main.pre_validation_checks')
    @patch('main.export_artifacts')
    @patch('main.validate_artifacts')
    @patch('main.visualize_artifacts')
    @patch('main.get_topology')
    @patch('main.qualification_report')
    @patch('main.parse_json')
    @patch('main.write_json')
    # noqa pylint: disable=too-many-arguments, too-many-locals, unused-argument, too-many-positional-arguments
    def test_main_flow(self, mock_write_json, mock_parse_json,
                       mock_qualification_report, mock_get_topology,
                       mock_visualize_artifacts, mock_validate_artifacts,
                       mock_export_artifacts, mock_pre_validation_checks,
                       mock_parse_config, mock_arg_parser):
        """
        Test the main flow of the script.
        """
        # Mock command line arguments
        mock_args = MagicMock()
        mock_args.resources = 'all'
        mock_args.skip_target_validation = False
        mock_arg_parser.return_value.parse_args.return_value = mock_args

        # Mock config files
        mock_cfg = MagicMock()
        mock_cfg.get.return_value = 'OPDK'
        mock_backend_cfg = MagicMock()
        mock_parse_config.side_effect = [mock_cfg, mock_backend_cfg]

        # Mock pre_validation_checks to return True
        mock_pre_validation_checks.return_value = True

        # Mock parse_json to return empty dicts initially
        mock_parse_json.side_effect = [{}, {}]

        # Mock export_artifacts to return some data
        mock_export_artifacts.return_value = {'export': True}

        # Mock validate_artifacts to return some data
        mock_validate_artifacts.return_value = {'report': True}

        # Mock get_topology to return some data
        mock_get_topology.return_value = {}

        # Call the main function
        main()

        # Assert that the core functions were called
        mock_pre_validation_checks.assert_called_once()
        mock_export_artifacts.assert_called_once()
        mock_validate_artifacts.assert_called_once()
        mock_visualize_artifacts.assert_called_once()
        mock_get_topology.assert_called_once()
        mock_qualification_report.assert_called_once()


if __name__ == '__main__':
    unittest.main()
