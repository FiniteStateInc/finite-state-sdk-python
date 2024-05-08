from unittest.mock import patch
from finite_state_sdk import get_asset_versions, queries


class TestGetAssetVersions:
    # Define test data
    auth_token = "your_auth_token"
    organization_context = "your_organization_context"
    asset_version_id = "your_asset_version_id"
    asset_id = "your_asset_id"
    business_unit_id = "your_business_unit_id"

    # Define mock response for the mocked function
    mock_response_data = [{"asset_version_id": "your_asset_version_id", "version": "1.0"}, {"asset_version_id": "your_asset_version_id_2", "version": "1.1"}]

    @patch("finite_state_sdk.get_all_paginated_results", return_value=mock_response_data)
    def test_get_asset_versions(self, mock_get_all_paginated_results):
        # Call the function
        result = get_asset_versions(
            token=self.auth_token,
            organization_context=self.organization_context,
            asset_version_id=self.asset_version_id,
            asset_id=self.asset_id,
            business_unit_id=self.business_unit_id
        )

        # Assertions
        expected_query = queries.ALL_ASSET_VERSIONS['query']
        expected_variables = queries.ALL_ASSET_VERSIONS['variables'](
            asset_version_id=self.asset_version_id,
            asset_id=self.asset_id,
            business_unit_id=self.business_unit_id
        )
        mock_get_all_paginated_results.assert_called_once_with(
            self.auth_token,
            self.organization_context,
            expected_query,
            expected_variables,
            'allAssetVersions'
        )

        assert result == self.mock_response_data
