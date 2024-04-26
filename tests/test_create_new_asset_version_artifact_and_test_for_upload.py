import pytest
from unittest.mock import patch, MagicMock
from finite_state_sdk import create_new_asset_version_artifact_and_test_for_upload, UploadMethod

class TestCreateAssetVersionArtifactAndTestForUpload:
    # Define test data
    auth_token = "your_auth_token"
    organization_context = "your_organization_context"
    business_unit_id = "business_unit_id"
    created_by_user_id = "user_id"
    asset_id = "asset_id"
    version = "version"
    product_id = "product_id"
    artifact_description = "artifact_description"
    upload_method = UploadMethod.API

    # Define mock responses for each mocked function
    mock_response_create_asset_version_on_asset = {
        "createNewAssetVersionOnAsset": {
            "assetVersion": {
                "id": "asset_version_id"
            }
        }
    }
    mock_response_create_asset_version = {
        "createNewAssetVersionOnAsset": {
            "assetVersion": {
                "id": "asset_version_id"
            }
        }
    }

    mock_response_create_artifact = {
        "createArtifact": {
            "id": "artifact_id"
        }
    }

    mock_response_create_test = {
        "createTest": {
            "id": "test_id"
        }
    }

    @patch("finite_state_sdk.create_asset_version_on_asset")
    @patch("finite_state_sdk.create_artifact")
    @patch("finite_state_sdk.create_test_as_binary_analysis")
    @patch("finite_state_sdk.create_test_as_third_party_scanner")
    @patch("finite_state_sdk.send_graphql_query")
    @patch("finite_state_sdk.get_all_assets")
    def test_create_new_asset_version_artifact_and_test_for_upload_binary_analysis(self, mock_get_all_assets, mock_send_query, mock_create_test_third_party_scanner, mock_create_test_binary_analysis, mock_create_artifact, mock_create_asset_version_on_asset):
        mock_get_all_assets.return_value = [{"name": "asset_name", "ctx": {"products": []}}]
        mock_send_query.side_effect = [self.mock_response_create_asset_version, self.mock_response_create_artifact, self.mock_response_create_test]
        mock_create_asset_version_on_asset.return_value = self.mock_response_create_asset_version_on_asset
        mock_create_artifact.return_value = self.mock_response_create_artifact
        mock_create_test_binary_analysis.return_value = self.mock_response_create_test
        mock_create_test_third_party_scanner.return_value = self.mock_response_create_test

        response = create_new_asset_version_artifact_and_test_for_upload(
            token=self.auth_token,
            organization_context=self.organization_context,
            business_unit_id=self.business_unit_id,
            created_by_user_id=self.created_by_user_id,
            asset_id=self.asset_id,
            version=self.version,
            product_id=self.product_id,
            test_type="finite_state_binary_analysis",
            artifact_description=self.artifact_description,
            upload_method=self.upload_method
        )

        mock_get_all_assets.assert_called_once()
        mock_send_query.assert_called()
        mock_create_asset_version_on_asset.assert_called_once()
        mock_create_artifact.assert_called_once()
        mock_create_test_binary_analysis.assert_called_once()
        mock_create_test_third_party_scanner.assert_not_called()

        assert response == self.mock_response_create_test['id']

    @patch("finite_state_sdk.create_asset_version_on_asset")
    @patch("finite_state_sdk.create_artifact")
    @patch("finite_state_sdk.create_test_as_binary_analysis")
    @patch("finite_state_sdk.create_test_as_third_party_scanner")
    @patch("finite_state_sdk.send_graphql_query")
    @patch("finite_state_sdk.get_all_assets")
    def test_create_new_asset_version_artifact_and_test_for_upload_third_party_scanner(self, mock_get_all_assets, mock_send_query, mock_create_test_third_party_scanner, mock_create_test_binary_analysis, mock_create_artifact, mock_create_asset_version_on_asset):
        mock_get_all_assets.return_value = [{"name": "asset_name", "ctx": {"products": []}}]
        mock_send_query.side_effect = [self.mock_response_create_asset_version, self.mock_response_create_artifact, self.mock_response_create_test]
        mock_create_asset_version_on_asset.return_value = self.mock_response_create_asset_version_on_asset
        mock_create_artifact.return_value = self.mock_response_create_artifact
        mock_create_test_binary_analysis.return_value = self.mock_response_create_test
        mock_create_test_third_party_scanner.return_value = self.mock_response_create_test

        response = create_new_asset_version_artifact_and_test_for_upload(
            token=self.auth_token,
            organization_context=self.organization_context,
            business_unit_id=self.business_unit_id,
            created_by_user_id=self.created_by_user_id,
            asset_id=self.asset_id,
            version=self.version,
            product_id=self.product_id,
            test_type="third_party_scanner",
            artifact_description=self.artifact_description,
            upload_method=self.upload_method
        )

        mock_get_all_assets.assert_called_once()
        mock_create_asset_version_on_asset.assert_called_once()
        mock_create_artifact.assert_called_once()
        mock_create_test_binary_analysis.assert_not_called()
        mock_create_test_third_party_scanner.assert_called_once()

        assert response == self.mock_response_create_test['createTest']['id']
