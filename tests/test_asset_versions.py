from unittest import TestCase
from unittest.mock import patch

from finite_state_sdk import create_asset_version_on_asset


class TestAssetVersions(TestCase):
    # Define test data
    auth_token = "your_auth_token"
    organization_context = "your_organization_context"
    created_by_user_id = "user_id"
    asset_id = "asset_id"
    asset_version_name = "asset_version_name"

    # Define a mock response
    mock_response = {
        "data": {
            "AssetVersion": {
                "id": "mock_asset_version_id",
                "name": asset_version_name,
                "asset": {
                    "id": asset_id,
                    "name": "asset_name"
                },
                "createdBy": {
                    "id": created_by_user_id,
                    "email": "user@example.com"
                },
                "ctx": {
                    "asset": "asset_context",
                    "businessUnits": [],
                    "products": []
                }
            }
        }
    }

    @patch("finite_state_sdk.send_graphql_query")
    def test_create_asset_version_on_asset(self, mock_send_query):
        mock_send_query.return_value = self.mock_response
        response = create_asset_version_on_asset(
            self.auth_token,
            self.organization_context,
            self.created_by_user_id,
            self.asset_id,
            self.asset_version_name
        )
        mock_send_query.assert_called_once_with(
            self.auth_token,
            self.organization_context,
            """
        mutation BapiCreateAssetVersion_SDK($assetVersionName: String!, $assetId: ID!, $createdByUserId: ID!) {
            createNewAssetVersionOnAsset(assetVersionName: $assetVersionName, assetId: $assetId, createdByUserId: $createdByUserId) {
                id
                assetVersion {
                    id
                }
            }
        }
    """,
            {"assetVersionName": self.asset_version_name, "assetId": self.asset_id, "createdByUserId": self.created_by_user_id},
        )
        self.assertEqual(response, self.mock_response['data'])
