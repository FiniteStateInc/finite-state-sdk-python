import pytest
from unittest.mock import patch
from finite_state_sdk import create_asset

class TestCreateAsset:
    # Define test data
    auth_token = "your_auth_token"
    organization_context = "your_organization_context"
    business_unit_id = "business_unit_id"
    created_by_user_id = "user_id"
    asset_name = "asset_name"
    product_id = "product_id"

    # Define a mock response
    mock_response = {
        "data": {
            "createAsset": {
                "id": "mock_asset_id",
                "name": "asset_name",
                "dependentProducts": [],
                "group": {
                    "id": "business_unit_id",
                    "name": "business_unit_name"
                },
                "createdBy": {
                    "id": "user_id",
                    "email": "user@example.com"
                },
                "ctx": {
                    "asset": "mock_asset_id",
                    "products": ["product_id"],
                    "businessUnits": ["business_unit_id"]
                }
            }
        }
    }

    @patch("finite_state_sdk.send_graphql_query")
    def test_create_asset(self, mock_send_query):
        mock_send_query.return_value = self.mock_response
        response = create_asset(
            token=self.auth_token,
            organization_context=self.organization_context,
            business_unit_id=self.business_unit_id,
            created_by_user_id=self.created_by_user_id,
            asset_name=self.asset_name,
            product_id=self.product_id
        )
        mock_send_query.assert_called_once()

        assert response['createAsset']['id'] == self.mock_response['data']['createAsset']['id']
        assert response['createAsset']['name'] == self.mock_response['data']['createAsset']['name']
        assert response['createAsset']['dependentProducts'] == self.mock_response['data']['createAsset']['dependentProducts']
        assert response['createAsset']['group']['id'] == self.mock_response['data']['createAsset']['group']['id']
        assert response['createAsset']['group']['name'] == self.mock_response['data']['createAsset']['group']['name']
        assert response['createAsset']['createdBy']['id'] == self.mock_response['data']['createAsset']['createdBy']['id']
        assert response['createAsset']['createdBy']['email'] == self.mock_response['data']['createAsset']['createdBy']['email']
        assert response['createAsset']['ctx']['asset'] == self.mock_response['data']['createAsset']['ctx']['asset']
        assert response['createAsset']['ctx']['products'] == self.mock_response['data']['createAsset']['ctx']['products']
        assert response['createAsset']['ctx']['businessUnits'] == self.mock_response['data']['createAsset']['ctx']['businessUnits']
