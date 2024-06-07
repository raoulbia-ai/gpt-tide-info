#TODO modify in light of added param to get_google_sheet()
import unittest
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import get_google_sheet

class TestGoogleSheetsConnection(unittest.TestCase):
    @patch('app.gspread.authorize')
    @patch('app.ServiceAccountCredentials.from_json_keyfile_name')
    def test_get_google_sheet(self, mock_from_json_keyfile_name, mock_authorize):
        # Arrange
        mock_client = MagicMock()
        mock_authorize.return_value = mock_client
        mock_sheet = MagicMock()
        mock_client.open.return_value = mock_sheet
        mock_sheet1 = MagicMock()
        mock_sheet.sheet1 = mock_sheet1

        # Act
        result = get_google_sheet()

        # Assert
        mock_from_json_keyfile_name.assert_called_once()
        mock_authorize.assert_called_once()
        # mock_client.open.assert_called_once_with("tides_web_scraped")
        mock_client.open.assert_called_once_with("tv_guide_arte")
        self.assertEqual(result, mock_sheet1)

if __name__ == '__main__':
    unittest.main()