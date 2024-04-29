from unittest.mock import patch
from finite_state_sdk import get_assets, queries


class TestGetAssets:
    # Define test data
    auth_token = "your_auth_token"
    organization_context = "your_organization_context"
    asset_id = "your_asset_id"
    business_unit_id = "your_business_unit_id"

    # Define mock response for the mocked function
    mock_response_data = [{"asset_id": "your_asset_id", "name": "asset1"}, {"asset_id": "your_asset_id_2", "name": "asset2"}]

    @patch("finite_state_sdk.get_all_paginated_results", return_value=mock_response_data)
    def test_get_assets(self, mock_get_all_paginated_results):
        # Call the function
        result = get_assets(
            token=self.auth_token,
            organization_context=self.organization_context,
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
