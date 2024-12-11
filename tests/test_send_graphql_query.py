import pytest
from unittest.mock import patch, MagicMock
from finite_state_sdk import send_graphql_query
from finite_state_sdk.utils import BreakoutException
import tenacity


class TestSendGraphQLQuery:
    # Define test data
    token = "mock_token"
    organization_context = "mock_organization_context"
    # Use a valid GraphQL query
    query = """
    query {
        someField {
            subField
        }
    }
    """

    mutation = """
    mutation {
        createItem(input: {name: "mock_item"}) {
            id
            name
        }
    }
    """
    variables = {"var1": "value1", "var2": "value2"}
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
        "Organization-Context": organization_context,
    }

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
            headers=self.headers,
            json={"query": self.query, "variables": self.variables},
        )
        assert result == {"data": {"result": "mock_result"}}

    @patch("finite_state_sdk.requests.post")
    def test_send_graphql_query_graphql_error(self, mock_post):
        # Mock response with GraphQL errors
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"errors": [{"message": "GraphQL error occurred"}]}
        mock_post.return_value = mock_response

        # Call the function and expect a BreakoutException
        with pytest.raises(BreakoutException) as excinfo:
            send_graphql_query(self.token, self.organization_context, self.query, self.variables)

        assert "Error: [{'message': 'GraphQL error occurred'}]" in str(excinfo.value)

    @patch("finite_state_sdk.requests.post")
    def test_send_graphql_query_internal_server_error(self, mock_post):
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_response.json.return_value = {"error": "Internal Server Error"}
        mock_post.return_value = mock_response

        # Call the function and expect a RetryError
        with pytest.raises(tenacity.RetryError) as excinfo:
            send_graphql_query(self.token, self.organization_context, self.query, self.variables)

        # Check the inner exception message
        inner_exception = excinfo.value.last_attempt.exception()
        assert "Error: 500 - Internal Server Error" in str(inner_exception)

    @patch("finite_state_sdk.requests.post")
    def test_send_graphql_query_mutation_success(self, mock_post):
        # Mock response for mutation
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": {"createItem": {"id": "1", "name": "mock_item"}}}
        mock_post.return_value = mock_response

        # Call the function
        result = send_graphql_query(self.token, self.organization_context, self.mutation, {})

        # Assertions
        mock_post.assert_called_once_with(
            "https://platform.finitestate.io/api/v1/graphql",
            headers=self.headers,
            json={"query": self.mutation, "variables": {}},
        )
        assert result == {"data": {"createItem": {"id": "1", "name": "mock_item"}}}

    @patch("finite_state_sdk.requests.post")
    def test_send_graphql_query_mutation_no_retry(self, mock_post):
        # Mock response for mutation failure
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"errors": [{"message": "Mutation error occurred"}]}
        mock_post.return_value = mock_response

        # Call the function and expect a BreakoutException
        with pytest.raises(BreakoutException) as excinfo:
            send_graphql_query(self.token, self.organization_context, self.mutation, {})

        # Check the error message
        assert "Error: [{'message': 'Mutation error occurred'}]" in str(excinfo.value)
        mock_post.assert_called_once()  # Ensure that the post was called only once

    @patch("finite_state_sdk.requests.post")
    def test_send_graphql_query_mutation_internal_server_error(self, mock_post):
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_response.json.return_value = {"error": "Internal Server Error"}
        mock_post.return_value = mock_response

        # Call the function and expect a RetryError
        with pytest.raises(BreakoutException) as excinfo:
            send_graphql_query(self.token, self.organization_context, self.mutation, {})

        assert "Error: 500 - Internal Server Error" in str(excinfo.value)
