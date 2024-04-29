from unittest.mock import patch
from finite_state_sdk import get_all_artifacts, queries


class TestGetAllArtifacts:
    # Define test data
    auth_token = "your_auth_token"
    organization_context = "your_organization_context"
    artifact_id = "optional_artifact_id"
    business_unit_id = "optional_business_unit_id"

    # Define mock response for the mocked function
    mock_response_data = ["artifact1", "artifact2", "artifact3"]

    @patch("finite_state_sdk.get_all_paginated_results", return_value=mock_response_data)
    def test_get_all_artifacts(self, mock_get_all_paginated_results):
        # Call the function
        result = get_all_artifacts(
            self.auth_token,
            self.organization_context,
            artifact_id=self.artifact_id,
            business_unit_id=self.business_unit_id
        )

        # Assertions
        mock_get_all_paginated_results.assert_called_once_with(
            self.auth_token,
            self.organization_context,
            queries.ALL_ARTIFACTS['query'],
            queries.ALL_ARTIFACTS['variables'](self.artifact_id, self.business_unit_id),
            'allAssets'
        )
        assert result == self.mock_response_data
