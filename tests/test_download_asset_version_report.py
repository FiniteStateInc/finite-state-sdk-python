import pytest
from unittest.mock import patch, MagicMock
from finite_state_sdk import download_asset_version_report

class TestDownloadAssetVersionReport:
    # Define test data
    auth_token = "your_auth_token"
    organization_context = "your_organization_context"
    asset_version_id = "asset_version_id"
    report_type = "CSV"
    report_subtype = "ALL_FINDINGS"
    output_filename = "test_report.csv"
    verbose = False

    # Define mock response for the mocked function
    mock_response_content = b"mock_report_content"
    mock_response_status_code = 200

    @patch("finite_state_sdk.generate_report_download_url", return_value="mock_download_url")
    @patch("finite_state_sdk.requests.get")
    @patch("builtins.open", MagicMock())
    def test_download_asset_version_report_success(self, mock_get, mock_generate_url):
        # Mock the response from the requests.get call
        mock_response = MagicMock()
        mock_response.status_code = self.mock_response_status_code
        mock_response.content = self.mock_response_content
        mock_get.return_value = mock_response

        # Call the function
        download_asset_version_report(
            self.auth_token,
            self.organization_context,
            asset_version_id=self.asset_version_id,
            report_type=self.report_type,
            report_subtype=self.report_subtype,
            output_filename=self.output_filename,
            verbose=self.verbose
        )

        # Assertions
        mock_generate_url.assert_called_once_with(
            self.auth_token,
            self.organization_context,
            asset_version_id=self.asset_version_id,
            report_type=self.report_type,
            report_subtype=self.report_subtype,
            verbose=self.verbose
        )
        mock_get.assert_called_once_with("mock_download_url")
        assert mock_response.status_code == self.mock_response_status_code
        assert mock_response.content == self.mock_response_content

    @patch("finite_state_sdk.generate_report_download_url", return_value="mock_download_url")
    @patch("finite_state_sdk.requests.get")
    @patch("builtins.open", MagicMock())
    def test_download_asset_version_report_failure(self, mock_get, mock_generate_url):
        # Mock the response from the requests.get call
        mock_response = MagicMock()
        mock_response.status_code = 404  # Simulate a failed request
        mock_get.return_value = mock_response

        # Call the function and expect an Exception to be raised
        with pytest.raises(Exception) as e:
            download_asset_version_report(
                self.auth_token,
                self.organization_context,
                asset_version_id=self.asset_version_id,
                report_type=self.report_type,
                report_subtype=self.report_subtype,
                output_filename=self.output_filename,
                verbose=self.verbose
            )

        # Assertions
        mock_generate_url.assert_called_once_with(
            self.auth_token,
            self.organization_context,
            asset_version_id=self.asset_version_id,
            report_type=self.report_type,
            report_subtype=self.report_subtype,
            verbose=self.verbose
        )
        mock_get.assert_called_once_with("mock_download_url")
        assert str(e.value) == f"Failed to download the file. Status code: {mock_response.status_code}"

