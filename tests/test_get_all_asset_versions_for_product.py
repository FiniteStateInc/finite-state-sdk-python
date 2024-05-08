from unittest.mock import patch
from finite_state_sdk import get_all_asset_versions_for_product, queries


class TestGetAllAssetVersionsForProduct:
    # Define test data
    auth_token = "your_auth_token"
    organization_context = "your_organization_context"
    product_id = "your_product_id"

    # Define mock response for the mocked function
    mock_response_data = ["asset_version1", "asset_version2", "asset_version3"]

    @patch("finite_state_sdk.get_all_paginated_results", return_value=mock_response_data)
    def test_get_all_asset_versions_for_product(self, mock_get_all_paginated_results):
        # Call the function
        result = get_all_asset_versions_for_product(
            token=self.auth_token,
            organization_context=self.organization_context,
            product_id=self.product_id
        )

        # Assertions
        expected_query = queries.ONE_PRODUCT_ALL_ASSET_VERSIONS['query']
        expected_variables = queries.ONE_PRODUCT_ALL_ASSET_VERSIONS['variables'](self.product_id)
        mock_get_all_paginated_results.assert_called_once_with(
            self.auth_token,
            self.organization_context,
            expected_query,
            expected_variables,
            'allProducts'
        )

        assert result == self.mock_response_data
