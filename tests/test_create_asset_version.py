import pytest
from unittest.mock import patch
from finite_state_sdk import create_asset_version

class TestCreateAssetVersion:
    # Define test data
    auth_token = "your_auth_token"
    organization_context = "your_organization_context"
    business_unit_id = "business_unit_id"
    created_by_user_id = "user_id"
    asset_id = "asset_id"
    asset_version_name = "asset_version_name"
    product_id = "product_id"

    # Define a mock response
    mock_response = {
        "data": {
            "createAssetVersion": {
                "id": "mock_asset_version_id",
                "name": "asset_version_name",
                "asset": {
                    "id": "asset_id",
                    "name": "asset_name"
                },
                "createdBy": {
                    "id": "user_id",
                    "email": "user@example.com"
                },
                "ctx": {
                    "asset": "asset_id",
                    "products": ["product_id"],
                    "businessUnits": ["business_unit_id"]
                }
            }
        }
    }

    @patch("finite_state_sdk.send_graphql_query")
    def test_create_asset_version(self, mock_send_query):
        mock_send_query.return_value = self.mock_response
        response = create_asset_version(
            token=self.auth_token,
            organization_context=self.organization_context,
            business_unit_id=self.business_unit_id,
            created_by_user_id=self.created_by_user_id,
            asset_id=self.asset_id,
            asset_version_name=self.asset_version_name,
            product_id=self.product_id
        )
        mock_send_query.assert_called_once()

        assert response['createAssetVersion']['id'] == self.mock_response['data']['createAssetVersion']['id']
        assert response['createAssetVersion']['name'] == self.mock_response['data']['createAssetVersion']['name']
        assert response['createAssetVersion']['asset']['id'] == self.mock_response['data']['createAssetVersion']['asset']['id']
        assert response['createAssetVersion']['asset']['name'] == self.mock_response['data']['createAssetVersion']['asset']['name']
        assert response['createAssetVersion']['createdBy']['id'] == self.mock_response['data']['createAssetVersion']['createdBy']['id']
        assert response['createAssetVersion']['createdBy']['email'] == self.mock_response['data']['createAssetVersion']['createdBy']['email']
        assert response['createAssetVersion']['ctx']['asset'] == self.mock_response['data']['createAssetVersion']['ctx']['asset']
        assert response['createAssetVersion']['ctx']['products'] == self.mock_response['data']['createAssetVersion']['ctx']['products']
        assert response['createAssetVersion']['ctx']['businessUnits'] == self.mock_response['data']['createAssetVersion']['ctx']['businessUnits']
