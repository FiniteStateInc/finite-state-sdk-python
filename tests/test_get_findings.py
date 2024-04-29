from unittest.mock import patch
from finite_state_sdk import get_findings, queries


class TestGetFindings:
    # Define test data
    auth_token = "mock_auth_token"
    organization_context = "mock_organization_context"
    asset_version_id = "mock_asset_version_id"
    finding_id = "mock_finding_id"
    category = "mock_category"
    status = "mock_status"
    severity = "mock_severity"
    limit = 100

    @patch("finite_state_sdk.send_graphql_query")
    def test_get_findings_not_count(self, mock_send_graphql_query):
        # Mock response object
        mock_send_graphql_query.return_value = {"data": {"_allFindingsMeta": {"count": 3}}}

        # Call the function
        result = get_findings(self.auth_token, self.organization_context, self.asset_version_id, self.finding_id,
                              self.category, self.status, self.severity, True, self.limit)

        # Define expected query and variables
        expected_query = queries.GET_FINDINGS_COUNT['query']
        expected_variables = queries.GET_FINDINGS_COUNT['variables'](
            asset_version_id=self.asset_version_id,
            finding_id=self.finding_id,
            category=self.category,
            status=self.status,
            severity=self.severity,
            limit=self.limit
        )

        # Assertions
        mock_send_graphql_query.assert_called_once_with(
            self.auth_token,
            self.organization_context,
            expected_query,
            expected_variables,
        )
        assert result == {"count": 3}

    @patch("finite_state_sdk.get_all_paginated_results")
    def test_get_findings_count(self, mock_get_all_paginated_results):
        # Mock response object
        mock_get_all_paginated_results.return_value = [{"id": "finding1"}, {"id": "finding2"}, {"id": "finding3"}]

        # Call the function
        result = get_findings(self.auth_token, self.organization_context, self.asset_version_id, self.finding_id,
                              self.category, self.status, self.severity, False, self.limit)

        # Define expected query and variables
        expected_query = queries.GET_FINDINGS['query']
        expected_variables = queries.GET_FINDINGS['variables'](
            asset_version_id=self.asset_version_id,
            finding_id=self.finding_id,
            category=self.category,
            status=self.status,
            severity=self.severity,
            limit=self.limit
        )

        # Assertions
        mock_get_all_paginated_results.assert_called_once_with(
            self.auth_token,
            self.organization_context,
            expected_query,
            expected_variables,
            'allFindings',
            limit=self.limit
        )
        assert result == [{"id": "finding1"}, {"id": "finding2"}, {"id": "finding3"}]

