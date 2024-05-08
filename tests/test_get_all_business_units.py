from unittest.mock import patch
from finite_state_sdk import get_all_business_units, queries


class TestGetAllBusinessUnits:
    # Define test data
    auth_token = "your_auth_token"
    organization_context = "your_organization_context"

    # Define mock response for the mocked function
    mock_response_data = ["business_unit1", "business_unit2", "business_unit3"]

    @patch("finite_state_sdk.get_all_paginated_results", return_value=mock_response_data)
    def test_get_all_business_units(self, mock_get_all_paginated_results):
        # Call the function
        result = get_all_business_units(
            token=self.auth_token,
            organization_context=self.organization_context
        )

        # Assertions
        expected_query = queries.ALL_BUSINESS_UNITS['query']
        expected_variables = queries.ALL_BUSINESS_UNITS['variables']
        mock_get_all_paginated_results.assert_called_once_with(
            self.auth_token,
            self.organization_context,
            expected_query,
            expected_variables,
            'allGroups'
        )

        assert result == self.mock_response_data
