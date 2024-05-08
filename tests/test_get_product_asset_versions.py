import pytest
from unittest.mock import patch
from finite_state_sdk import get_product_asset_versions, queries


class TestGetProductAssetVersions:
    # Define test data
    auth_token = "mock_auth_token"
    organization_context = "mock_organization_context"
    product_id = "mock_product_id"

    @patch("finite_state_sdk.get_all_paginated_results")
    def test_get_product_asset_versions(self, mock_get_all_paginated_results):
        # Call the function
        result = get_product_asset_versions(self.auth_token, self.organization_context, self.product_id)

        # Define expected query and variables
        expected_query = queries.GET_PRODUCT_ASSET_VERSIONS['query']
        expected_variables = queries.GET_PRODUCT_ASSET_VERSIONS['variables'](self.product_id)

        # Assertions
        mock_get_all_paginated_results.assert_called_once_with(
            self.auth_token,
            self.organization_context,
            expected_query,
            expected_variables,
            'allProducts'
        )
        assert result == mock_get_all_paginated_results.return_value

    @patch("finite_state_sdk.get_all_paginated_results")
    def test_get_product_asset_versions_no_product_id(self, mock_get_all_paginated_results):
        # Call the function without providing product_id
        with pytest.raises(Exception) as e:
            get_product_asset_versions(self.auth_token, self.organization_context)

        # Assertion
        assert str(e.value) == "Product ID is required"
