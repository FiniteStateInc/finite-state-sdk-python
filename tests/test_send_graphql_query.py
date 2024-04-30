import pytest
from unittest.mock import patch, MagicMock
from finite_state_sdk import send_graphql_query


class TestSendGraphQLQuery:
    # Define test data
    token = "mock_token"
    organization_context = "mock_organization_context"
    query = "mock_query"
    variables = {"var1": "value1", "var2": "value2"}

    @patch("finite_state_sdk.requests.post")
    def test_send_graphql_query_success(self, mock_post):
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": {"result": "mock_result"}}
        mock_post.return_value = mock_response

        # Call the function
        result = send_graphql_query(self.token, self.organization_context, self.query, self.variables)

        # Assertions
        mock_post.assert_called_once_with(
            "https://platform.finitestate.io/api/v1/graphql",
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.token}',
                'Organization-Context': self.organization_context
            },
            json={'query': self.query, 'variables': self.variables}
        )
        assert result == {"data": {"result": "mock_result"}}

    @patch("finite_state_sdk.requests.post")
    def test_send_graphql_query_error(self, mock_post):
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_response.json.return_value = {"error": "Internal Server Error"}
        mock_post.return_value = mock_response

        # Call the function and expect an exception
        with pytest.raises(Exception) as excinfo:
            send_graphql_query(self.token, self.organization_context, self.query, self.variables)

        # Assertion
        assert str(excinfo.value) == "Error: 500 - Internal Server Error"
