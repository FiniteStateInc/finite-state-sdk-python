from unittest.mock import patch
from finite_state_sdk import get_all_assets, queries


class TestGetAllAssets:
    # Define test data
    auth_token = "your_auth_token"
    organization_context = "your_organization_context"
    asset_id = "optional_asset_id"
    business_unit_id = "optional_business_unit_id"

    # Define mock response for the mocked function
    mock_response_data = ["asset1", "asset2", "asset3"]

    @patch("finite_state_sdk.get_all_paginated_results", return_value=mock_response_data)
    def test_get_all_assets(self, mock_get_all_paginated_results):
        # Call the function
        result = get_all_assets(
            self.auth_token,
            self.organization_context,
            asset_id=self.asset_id,
            business_unit_id=self.business_unit_id
        )

        # Assertions
        expected_query = queries.ALL_ASSETS['query']
        expected_variables = queries.ALL_ASSETS['variables'](self.asset_id, self.business_unit_id)
        mock_get_all_paginated_results.assert_called_once_with(
            self.auth_token,
            self.organization_context,
            expected_query,
            expected_variables,
            'allAssets'
        )
        assert result == self.mock_response_data
