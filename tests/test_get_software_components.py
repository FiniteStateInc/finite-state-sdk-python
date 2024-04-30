from unittest.mock import patch
from finite_state_sdk import get_software_components, queries


class TestGetSoftwareComponents:
    # Define test data
    auth_token = "mock_auth_token"
    organization_context = "mock_organization_context"
    asset_version_id = "mock_asset_version_id"
    type = "APPLICATION"

    @patch("finite_state_sdk.get_all_paginated_results")
    def test_get_software_components(self, mock_get_all_paginated_results):
        # Call the function
        result = get_software_components(self.auth_token, self.organization_context, self.asset_version_id,
                                         type=self.type)

        # Define expected query and variables
        expected_query = queries.GET_SOFTWARE_COMPONENTS['query']
        expected_variables = queries.GET_SOFTWARE_COMPONENTS['variables'](asset_version_id=self.asset_version_id,
                                                                          type=self.type)

        # Assertions
        mock_get_all_paginated_results.assert_called_once_with(
            self.auth_token,
            self.organization_context,
            expected_query,
            expected_variables,
            'allSoftwareComponentInstances'
        )
        assert result == mock_get_all_paginated_results.return_value
