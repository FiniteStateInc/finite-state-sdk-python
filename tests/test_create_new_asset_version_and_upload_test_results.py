from unittest.mock import patch
from finite_state_sdk import create_new_asset_version_and_upload_test_results, UploadMethod


class TestCreateNewAssetVersionAndUploadTestResults:
    # Define test data
    auth_token = "your_auth_token"
    organization_context = "your_organization_context"
    business_unit_id = "business_unit_id"
    created_by_user_id = "user_id"
    asset_id = "asset_id"
    version = "version"
    file_path = "file_path"
    product_id = "product_id"
    test_type = "test_type"
    artifact_description = "artifact_description"
    upload_method = UploadMethod.API

    # Define mock responses for each mocked function
    mock_response_create_test = "test_id"

    @patch("finite_state_sdk.create_new_asset_version_artifact_and_test_for_upload")
    @patch("finite_state_sdk.upload_test_results_file")
    def test_create_new_asset_version_and_upload_test_results(self, mock_upload_file, mock_create_asset_version):
        mock_create_asset_version.return_value = self.mock_response_create_test
        mock_upload_file.return_value = {}

        response = create_new_asset_version_and_upload_test_results(
            self.auth_token,
            self.organization_context,
            business_unit_id=self.business_unit_id,
            created_by_user_id=self.created_by_user_id,
            asset_id=self.asset_id,
            version=self.version,
            file_path=self.file_path,
            product_id=self.product_id,
            test_type=self.test_type,
            artifact_description=self.artifact_description,
            upload_method=self.upload_method
        )

        mock_create_asset_version.assert_called_once_with(
            self.auth_token,
            self.organization_context,
            business_unit_id=self.business_unit_id,
            created_by_user_id=self.created_by_user_id,
            asset_id=self.asset_id,
            version=self.version,
            product_id=self.product_id,
            test_type=self.test_type,
            artifact_description=self.artifact_description,
            upload_method=self.upload_method
        )
        mock_upload_file.assert_called_once_with(
            self.auth_token,
            self.organization_context,
            test_id=self.mock_response_create_test,
            file_path=self.file_path
        )

        assert response == {}
