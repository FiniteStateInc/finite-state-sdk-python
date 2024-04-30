import pytest
from unittest.mock import patch, MagicMock
from finite_state_sdk import upload_bytes_to_url, upload_file_to_url


class TestUploadFunctions:
    url = "mock_url"
    bytes_data = b"mock_bytes"
    file_path = "mock_file_path"

    @patch("finite_state_sdk.requests.put")
    def test_upload_bytes_to_url_success(self, mock_requests_put):
        # Mock response for successful request
        mock_response = MagicMock(status_code=200)
        mock_requests_put.return_value = mock_response

        # Call the function
        result = upload_bytes_to_url(self.url, self.bytes_data)

        # Assertions
        mock_requests_put.assert_called_once_with(self.url, data=self.bytes_data)
        assert result == mock_response

    @patch("finite_state_sdk.requests.put")
    def test_upload_bytes_to_url_failure(self, mock_requests_put):
        # Mock response for failed request
        mock_response = MagicMock(status_code=500, text="Internal Server Error")
        mock_requests_put.return_value = mock_response

        # Call the function and expect an Exception
        with pytest.raises(Exception) as excinfo:
            upload_bytes_to_url(self.url, self.bytes_data)

        # Assertion
        assert str(excinfo.value) == f"Error: {mock_response.status_code} - {mock_response.text}"

    @patch("builtins.open")
    @patch("finite_state_sdk.requests.put")
    def test_upload_file_to_url_success(self, mock_requests_put, mock_open):
        # Mock response for successful request
        mock_response = MagicMock(status_code=200)
        mock_requests_put.return_value = mock_response
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        # Call the function
        result = upload_file_to_url(self.url, self.file_path)

        # Assertions
        mock_open.assert_called_once_with(self.file_path, 'rb')
        mock_requests_put.assert_called_once_with(self.url, data=mock_file)
        assert result == mock_response

    @patch("builtins.open")
    @patch("finite_state_sdk.requests.put")
    def test_upload_file_to_url_failure(self, mock_requests_put, mock_open):
        # Mock response for failed request
        mock_response = MagicMock(status_code=500, text="Internal Server Error")
        mock_requests_put.return_value = mock_response
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        # Call the function and expect an Exception
        with pytest.raises(Exception) as excinfo:
            upload_file_to_url(self.url, self.file_path)

        # Assertion
        mock_open.assert_called_once_with(self.file_path, 'rb')
        mock_requests_put.assert_called_once_with(self.url, data=mock_file)
        assert str(excinfo.value) == f"Error: {mock_response.status_code} - {mock_response.text}"
