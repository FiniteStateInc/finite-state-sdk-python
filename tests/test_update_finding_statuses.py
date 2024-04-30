import pytest
from unittest.mock import patch
from finite_state_sdk import update_finding_statuses


class TestUpdateFindingStatuses:
    token = "mock_token"
    organization_context = "mock_organization_context"
    user_id = "mock_user_id"
    finding_ids = ["mock_finding_id_1", "mock_finding_id_2"]
    status = "AFFECTED"

    @patch("finite_state_sdk.send_graphql_query")
    def test_update_finding_statuses_success(self, mock_send_graphql_query):
        # Mock response
        mock_response = {"data": {"updateFindingsStatuses": {"success": True}}}
        mock_send_graphql_query.return_value = mock_response

        # Call the function
        result = update_finding_statuses(self.token, self.organization_context, self.user_id, self.finding_ids, self.status)

        # Assertions
        mock_send_graphql_query.assert_called_once()

        assert result == mock_response

    @pytest.mark.parametrize(
        "missing_param",
        [("user_id", None), ("finding_ids", None), ("status", None)]
    )
    def test_update_finding_statuses_missing_params(self, missing_param):
        # Unpack missing parameter
        param_name, param_value = missing_param

        # Call the function and expect a ValueError
        with pytest.raises(ValueError) as excinfo:
            update_finding_statuses(
                self.token, self.organization_context,
                self.user_id if param_name != "user_id" else param_value,
                self.finding_ids if param_name != "finding_ids" else param_value,
                self.status if param_name != "status" else param_value
            )

        # Assertion
        assert str(excinfo.value) == f"{param_name.replace('_', ' ').title()} is required"
