from unittest.mock import patch
from finite_state_sdk import create_test_as_third_party_scanner, UploadMethod


class TestCreateTestAsThirdPartyScanner:
    # Define test data
    auth_token = "your_auth_token"
    organization_context = "your_organization_context"
    business_unit_id = "business_unit_id"
    created_by_user_id = "user_id"
    asset_id = "asset_id"
    artifact_id = "artifact_id"
    test_name = "test_name"
    product_id = "product_id"
    test_type = "scanner_type"
    upload_method = UploadMethod.API

    # Define mock response for the mocked function
    mock_response = {
        "data": {
            "createTest": {
                "id": "test_id",
                "name": "test_name",
                "artifactUnderTest": {
                    "id": "artifact_id",
                    "name": "artifact_name",
                    "assetVersion": {
                        "id": "asset_version_id",
                        "name": "asset_version_name",
                        "asset": {
                            "id": "asset_id",
                            "name": "asset_name",
                            "dependentProducts": [{"id": "product_id", "name": "product_name"}]
                        }
                    }
                },
                "createdBy": {
                    "id": "user_id",
                    "email": "user_email"
                },
                "ctx": {
                    "asset": "asset_id",
                    "products": ["product_id"],
                    "businessUnits": ["business_unit_id"]
                },
                "uploadMethod": "API"
            }
        }
    }

    @patch("finite_state_sdk.create_test")
    def test_create_test_as_third_party_scanner(self, mock_create_test):
        mock_create_test.return_value = self.mock_response['data']

        response = create_test_as_third_party_scanner(
            self.auth_token,
            self.organization_context,
            business_unit_id=self.business_unit_id,
            created_by_user_id=self.created_by_user_id,
            asset_id=self.asset_id,
            artifact_id=self.artifact_id,
            test_name=self.test_name,
            product_id=self.product_id,
            test_type=self.test_type,
            upload_method=self.upload_method
        )

        mock_create_test.assert_called_once_with(
            self.auth_token,
            self.organization_context,
            business_unit_id=self.business_unit_id,
            created_by_user_id=self.created_by_user_id,
            asset_id=self.asset_id,
            artifact_id=self.artifact_id,
            test_name=self.test_name,
            product_id=self.product_id,
            test_type=self.test_type,
            upload_method=self.upload_method
        )

        assert response == self.mock_response['data']
