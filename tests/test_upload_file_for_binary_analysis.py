import pytest
from unittest.mock import patch, mock_open
from finite_state_sdk import upload_file_for_binary_analysis


class TestUploadFileForBinaryAnalysis:
    token = "mock_token"
    organization_context = "mock_organization_context"
    test_id = "mock_test_id"
    file_path = "mock_file_path"

    @patch("finite_state_sdk.send_graphql_query")
    @patch("finite_state_sdk.upload_bytes_to_url")
    @patch("builtins.open", new_callable=mock_open, read_data="mock_file_data")
    def test_upload_file_for_binary_analysis_success(self, mock_open, mock_upload_bytes_to_url, mock_send_graphql_query):
        # Mock response for startMultipartUploadV2
        mock_start_response = {"data": {"startMultipartUploadV2": {"uploadId": "mock_upload_id", "key": "mock_key"}}}

        # Mock response for generateUploadPartUrlV2
        mock_generate_upload_response = {"data": {"generateUploadPartUrlV2": {"uploadUrl": "mock_upload_url"}}}

        # Mock response for completeMultipartUploadV2
        mock_complete_response = {"data": {"completeMultipartUploadV2": {"key": "mock_key"}}}

        # Mock response for launchBinaryUploadProcessing
        mock_launch_response = {"data": {"launchBinaryUploadProcessing": {"key": "mock_key"}}}

        # Assign the responses to the side_effect
        mock_send_graphql_query.side_effect = [mock_start_response, mock_generate_upload_response,
                                               mock_complete_response, mock_launch_response]

        # Call the function
        result = upload_file_for_binary_analysis(self.token, self.organization_context, self.test_id, self.file_path)

        # Assertions
        mock_open.assert_called_once_with(self.file_path, "rb")
        mock_start_call = mock_send_graphql_query.call_args_list[0]
        assert mock_start_call[0][3] == {"testId": self.test_id}
        mock_generate_call = mock_send_graphql_query.call_args_list[1]
        assert mock_generate_call[0][3] == {"partNumber": 1, "uploadId": "mock_upload_id", "uploadKey": "mock_key"}
        mock_upload_bytes_to_url.assert_called_once_with("mock_upload_url", "mock_file_data")
        mock_complete_call = mock_send_graphql_query.call_args_list[2]
        assert mock_complete_call[0][3]["uploadId"] == "mock_upload_id"
        assert mock_complete_call[0][3]["uploadKey"] == "mock_key"
        assert len(mock_complete_call[0][3]["partData"]) == 1
        assert mock_complete_call[0][3]["partData"][0]["PartNumber"] == 1
        mock_launch_call = mock_send_graphql_query.call_args_list[3]
        assert mock_launch_call[0][3] == {"key": "mock_key", "testId": self.test_id}
        assert result == mock_launch_response['data']

    @pytest.mark.parametrize(
        "missing_param",
        [("test_id", None), ("file_path", None)]
    )
    def test_upload_file_for_binary_analysis_missing_params(self, missing_param):
        # Unpack missing parameter
        param_name, param_value = missing_param

        # Call the function and expect a ValueError
        with pytest.raises(ValueError) as excinfo:
            upload_file_for_binary_analysis(
                self.token, self.organization_context,
                self.test_id if param_name != "test_id" else param_value,
                self.file_path if param_name != "file_path" else param_value
            )

        # Assertion
        assert str(excinfo.value) == f"{param_name.replace('_', ' ').title()} is required"
