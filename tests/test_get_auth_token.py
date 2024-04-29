import pytest
from unittest.mock import patch, MagicMock
from finite_state_sdk import get_auth_token, TOKEN_URL


class TestGetAuthToken:
    # Define test data
    client_id = "your_client_id"
    client_secret = "your_client_secret"
    mock_access_token = "mock_access_token"

    @patch("finite_state_sdk.requests.post")
    def test_get_auth_token_success(self, mock_post):
        # Mock response object
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"access_token": self.mock_access_token}
        mock_post.return_value = mock_response

        # Call the function
        result = get_auth_token(self.client_id, self.client_secret)

        # Assertions
        mock_post.assert_called_once_with(
            TOKEN_URL,
            data='{"client_id": "your_client_id", "client_secret": "your_client_secret", "audience": "https://platform.finitestate.io/api/v1/graphql", "grant_type": "client_credentials"}',
            headers={'content-type': 'application/json'}
        )
        assert result == self.mock_access_token

    @patch("finite_state_sdk.requests.post")
    def test_get_auth_token_error(self, mock_post):
        # Mock response object
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad request"
        mock_post.return_value = mock_response

        # Assertions
        with pytest.raises(Exception) as exc_info:
            get_auth_token(self.client_id, self.client_secret)

        assert str(exc_info.value) == "Error: 400 - Bad request"
