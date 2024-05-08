import pytest
from unittest.mock import patch
from finite_state_sdk import upload_test_results_file


class TestUploadTestResultsFile:
    token = "mock_token"
    organization_context = "mock_organization_context"
    test_id = "mock_test_id"
    file_path = "mock_file_path"

    @patch("finite_state_sdk.send_graphql_query")
    @patch("finite_state_sdk.upload_file_to_url")
    def test_upload_test_results_file_success(self, mock_upload_file_to_url, mock_send_graphql_query):
        # Mock response for generateSinglePartUploadUrl
        mock_generate_response = {"data": {"generateSinglePartUploadUrl": {"uploadUrl": "mock_upload_url", "key": "mock_key"}}}

        # Mock response for launchTestResultProcessing
        mock_launch_response = {"data": {"launchTestResultProcessing": {"key": "mock_key"}}}

        # Assign the responses to the side_effect
        mock_send_graphql_query.side_effect = [mock_generate_response, mock_launch_response]

        # Call the function
        result = upload_test_results_file(self.token, self.organization_context, self.test_id, self.file_path)

        # Assertions
        mock_generate_call = mock_send_graphql_query.call_args_list[0]
        assert mock_generate_call[0][3] == {"testId": self.test_id}
        mock_upload_file_to_url.assert_called_once_with("mock_upload_url", self.file_path)
        mock_launch_call = mock_send_graphql_query.call_args_list[1]
        assert mock_launch_call[0][3] == {"testId": self.test_id, "key": "mock_key"}
        assert result == mock_launch_response['data']

    @pytest.mark.parametrize(
        "missing_param",
        [("test_id", None), ("file_path", None)]
    )
    def test_upload_test_results_file_missing_params(self, missing_param):
        # Unpack missing parameter
        param_name, param_value = missing_param

        # Call the function and expect a ValueError
        with pytest.raises(ValueError) as excinfo:
            upload_test_results_file(
                self.token, self.organization_context,
                self.test_id if param_name != "test_id" else param_value,
                self.file_path if param_name != "file_path" else param_value
            )

        # Assertion
        assert str(excinfo.value) == f"{param_name.replace('_', ' ').title()} is required"
