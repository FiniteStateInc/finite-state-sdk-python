from unittest.mock import patch
from finite_state_sdk import get_artifact_context, queries


class TestGetArtifactContext:
    # Define test data
    auth_token = "your_auth_token"
    organization_context = "your_organization_context"
    artifact_id = "your_artifact_id"

    # Define mock response for the mocked function
    mock_response_data = [{"artifact_id": "your_artifact_id", "ctx": "your_context"}]

    @patch("finite_state_sdk.get_all_paginated_results", return_value=mock_response_data)
    def test_get_artifact_context(self, mock_get_all_paginated_results):
        # Call the function
        result = get_artifact_context(
            token=self.auth_token,
            organization_context=self.organization_context,
            artifact_id=self.artifact_id
        )

        # Assertions
        expected_query = queries.ALL_ARTIFACTS['query']
        expected_variables = queries.ALL_ARTIFACTS['variables'](self.artifact_id, None)
        mock_get_all_paginated_results.assert_called_once_with(
            self.auth_token,
            self.organization_context,
            expected_query,
            expected_variables,
            'allAssets'
        )

        assert result == self.mock_response_data[0]['ctx']
