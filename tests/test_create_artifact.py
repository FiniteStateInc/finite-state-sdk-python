from unittest.mock import patch

from finite_state_sdk import create_artifact


class TestArtifacts:
    # Define test data
    auth_token = "your_auth_token"
    organization_context = "your_organization_context"
    business_unit_id = "business_unit_id"
    created_by_user_id = "user_id"
    asset_version_id = "asset_version_id"
    artifact_name = "artifact_name"
    product_id = "product_id"

    # Define a mock response
    mock_response = {
        "data": {
            "createArtifact": {
                "id": "mock_artifact_id",
                "name": "artifact_name",
                "assetVersion": {
                    "id": "asset_version_id",
                    "name": "asset_version_name",
                    "asset": {
                        "id": "asset_id",
                        "name": "asset_name"
                    }
                },
                "createdBy": {
                    "id": "user_id",
                    "email": "user@example.com"
                },
                "ctx": {
                    "asset": "asset_version_id",
                    "products": ["product_id"],
                    "businessUnits": ["business_unit_id"]
                }
            }
        }
    }

    @patch("finite_state_sdk.send_graphql_query")
    def test_create_artifact(self, mock_send_query):
        mock_send_query.return_value = self.mock_response
        response = create_artifact(
            token=self.auth_token,
            organization_context=self.organization_context,
            business_unit_id=self.business_unit_id,
            created_by_user_id=self.created_by_user_id,
            asset_version_id=self.asset_version_id,
            artifact_name=self.artifact_name,
            product_id=self.product_id
        )
        mock_send_query.assert_called_once()

        assert response['createArtifact']['id'] == self.mock_response['data']['createArtifact']['id']
        assert response['createArtifact']['name'] == self.mock_response['data']['createArtifact']['name']
        assert response['createArtifact']['assetVersion']['id'] == self.mock_response['data']['createArtifact']['assetVersion']['id']
        assert response['createArtifact']['assetVersion']['name'] == self.mock_response['data']['createArtifact']['assetVersion']['name']
        assert response['createArtifact']['assetVersion']['asset']['id'] == self.mock_response['data']['createArtifact']['assetVersion']['asset']['id']
        assert response['createArtifact']['assetVersion']['asset']['name'] == self.mock_response['data']['createArtifact']['assetVersion']['asset']['name']
        assert response['createArtifact']['createdBy']['id'] == self.mock_response['data']['createArtifact']['createdBy']['id']
        assert response['createArtifact']['createdBy']['email'] == self.mock_response['data']['createArtifact']['createdBy']['email']
        assert response['createArtifact']['ctx']['asset'] == self.mock_response['data']['createArtifact']['ctx']['asset']
        assert response['createArtifact']['ctx']['products'] == self.mock_response['data']['createArtifact']['ctx']['products']
        assert response['createArtifact']['ctx']['businessUnits'] == self.mock_response['data']['createArtifact']['ctx']['businessUnits']

# Run the test...
