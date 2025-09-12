"""Test suite for topology."""
import os
import shutil
import sys
import unittest
from unittest.mock import MagicMock, patch

from topology import ApigeeTopology
sys.path.insert(0, '..')


class TestApigeeTopology(unittest.TestCase):
    """Test class for ApigeeTopology."""

    def setUp(self):
        """Set up."""
        self.mock_cfg = {
            'inputs': {
                'TARGET_DIR': 'target'
            }
        }
        self.mock_backend_cfg = {
            'topology': {
                'TOPOLOGY_DIR': 'topology',
                'NW_TOPOLOGY_MAPPING': 'nw_topology.json',
                'DATA_CENTER_MAPPING': 'dc_mapping.json'
            }
        }
        mock_cfg_instance = MagicMock()
        (mock_cfg_instance.get.
         side_effect) = lambda section, key: self.mock_cfg[section][key]
        with patch('utils.parse_config') as mock_parse_config, \
             patch('topology.ApigeeClassic') as mock_apigee_classic:
            mock_parse_config.side_effect = [self.mock_backend_cfg]
            self.topology = ApigeeTopology(
                baseurl="https://mock.baseurl",
                org="mock_org",
                token="mock_token",
                auth_type="basic",
                cfg=mock_cfg_instance
            )
            self.topology.opdk = mock_apigee_classic.return_value

    def tearDown(self):
        """Tear down."""
        if hasattr(self, 'topology') and os.path.exists(
                self.topology.topology_dir_path):
            shutil.rmtree(self.topology.topology_dir_path)

    @patch('topology.write_json')
    @patch('topology.pod_mapping', {'test-pod': {}})
    def test_get_topology_mapping(self, mock_write_json):
        """Test get_topology_mapping."""
        mock_response = [
            {
                "externalHostName": "host1.external",
                "externalIP": "1.1.1.1",
                "internalHostName": "host1.internal",
                "internalIP": "10.1.1.1",
                "isUp": True,
                "pod": "test-pod",
                "reachable": True,
                "region": "test-region",
                "type": ["test-type"]
            }
        ]
        self.topology.opdk.view_pod_component_details = MagicMock(
            return_value=mock_response)
        result = self.topology.get_topology_mapping()
        self.assertIn('test-pod', result)
        self.assertEqual(len(result['test-pod']), 1)
        self.assertEqual(result['test-pod'][0]['externalHostName'],
                         'host1.external')
        mock_write_json.assert_called_once()

    def test_get_data_center_mapping(self):
        """Test get_data_center_mapping."""
        pod_component_mapping = {
            "test-pod": [
                {
                    "region": "test-region",
                    "pod": "test-pod",
                    "internalIP": "10.1.1.1",
                    "type": ["test-type"]
                }
            ]
        }
        result = self.topology.get_data_center_mapping(pod_component_mapping)
        self.assertIn('test-region', result)
        self.assertIn('test-pod', result['test-region'])
        self.assertEqual(len(result['test-region']['test-pod']), 1)
        self.assertEqual(result['test-region']['test-pod'][0]['internalIP'],
                         '10.1.1.1')

    @patch('topology.Diagram')
    @patch('topology.Cluster')
    @patch('topology.Blank')
    @patch('topology.pod_mapping', {'test-pod': {'bgcolor': '#FFFFFF'}})
    def test_draw_topology_graph_diagram(self, mock_blank, mock_cluster,
                                         mock_diagram):
        """Test draw_topology_graph_diagram."""
        data_center = {
            "test-region": {
                "test-pod": [
                    {
                        "internalIP": "10.1.1.1",
                        "type": ["test-type"]
                    }
                ]
            }
        }
        self.topology.draw_topology_graph_diagram(data_center)
        self.assertEqual(mock_diagram.call_count, 2)
        self.assertEqual(mock_cluster.call_count, 5)
        mock_blank.assert_called()


if __name__ == '__main__':
    unittest.main()
