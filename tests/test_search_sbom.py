from unittest.mock import patch
from finite_state_sdk import search_sbom


class TestSearchSBOM:
    # Define test data
    auth_token = "mock_auth_token"
    organization_context = "mock_organization_context"
    name = "mock_name"
    version = "mock_version"
    asset_version_id = "mock_asset_version_id"
    search_method = "EXACT"
    case_sensitive = False

    @patch("finite_state_sdk.get_all_paginated_results")
    def test_search_sbom_exact_case_insensitive(self, mock_get_all_paginated_results):
        # Call the function
        result = search_sbom(self.auth_token, self.organization_context, self.name, self.version,
                             asset_version_id=self.asset_version_id, search_method=self.search_method,
                             case_sensitive=self.case_sensitive)

        # Assertions
        mock_get_all_paginated_results.assert_called_once()

        assert result == mock_get_all_paginated_results.return_value
