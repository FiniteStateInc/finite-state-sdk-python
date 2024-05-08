from unittest.mock import patch
from finite_state_sdk import get_all_organizations, queries


class TestGetAllOrganizations:
    # Define test data
    auth_token = "your_auth_token"
    organization_context = "your_organization_context"

    # Define mock response for the mocked function
    mock_response_data = ["organization1", "organization2", "organization3"]

    @patch("finite_state_sdk.get_all_paginated_results", return_value=mock_response_data)
    def test_get_all_organizations(self, mock_get_all_paginated_results):
        # Call the function
        result = get_all_organizations(
            token=self.auth_token,
            organization_context=self.organization_context
        )

        # Assertions
        expected_query = queries.ALL_ORGANIZATIONS['query']
        expected_variables = queries.ALL_ORGANIZATIONS['variables']
        mock_get_all_paginated_results.assert_called_once_with(
            self.auth_token,
            self.organization_context,
            expected_query,
            expected_variables,
            'allOrganizations'
        )

        assert result == self.mock_response_data
