from unittest.mock import patch
from finite_state_sdk import create_product


class TestCreateProduct:
    # Define test data
    auth_token = "your_auth_token"
    organization_context = "your_organization_context"
    business_unit_id = "business_unit_id"
    created_by_user_id = "user_id"
    product_name = "product_name"
    product_description = "product_description"
    vendor_id = "vendor_id"
    vendor_name = "vendor_name"

    # Define mock response for the mocked function
    mock_response = {
        "data": {
            "createProduct": {
                "id": "product_id",
                "name": "product_name",
                "vendor": {
                    "name": "vendor_name"
                },
                "group": {
                    "id": "business_unit_id",
                    "name": "business_unit_name"
                },
                "createdBy": {
                    "id": "user_id",
                    "email": "user_email"
                },
                "ctx": {
                    "businessUnit": "business_unit_id"
                }
            }
        }
    }

    @patch("finite_state_sdk.send_graphql_query")
    def test_create_product(self, mock_send_query):
        mock_send_query.return_value = self.mock_response

        response = create_product(
            token=self.auth_token,
            organization_context=self.organization_context,
            business_unit_id=self.business_unit_id,
            created_by_user_id=self.created_by_user_id,
            product_name=self.product_name,
            product_description=self.product_description,
            vendor_id=self.vendor_id,
            vendor_name=self.vendor_name
        )

        mock_send_query.assert_called_once()

        assert response == self.mock_response['data']
