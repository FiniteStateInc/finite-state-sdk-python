from unittest.mock import patch
from finite_state_sdk import get_products, queries


class TestGetProducts:
    # Define test data
    auth_token = "mock_auth_token"
    organization_context = "mock_organization_context"
    product_id = "mock_product_id"
    business_unit_id = "mock_business_unit_id"

    @patch("finite_state_sdk.get_all_paginated_results")
    def test_get_products(self, mock_get_all_paginated_results):
        # Call the function
        result = get_products(self.auth_token, self.organization_context)

        # Define expected query and variables
        expected_query = queries.GET_PRODUCTS['query']
        expected_variables = queries.GET_PRODUCTS['variables'](product_id=None, business_unit_id=None)

        # Assertions
        mock_get_all_paginated_results.assert_called_once_with(
            self.auth_token,
            self.organization_context,
            expected_query,
            expected_variables,
            'allProducts'
        )
        assert result == mock_get_all_paginated_results.return_value

    @patch("finite_state_sdk.get_all_paginated_results")
    def test_get_products_with_product_id(self, mock_get_all_paginated_results):
        # Call the function with product_id specified
        result = get_products(self.auth_token, self.organization_context, self.product_id)

        # Define expected query and variables
        expected_query = queries.GET_PRODUCTS['query']
        expected_variables = queries.GET_PRODUCTS['variables'](product_id=self.product_id, business_unit_id=None)

        # Assertions
        mock_get_all_paginated_results.assert_called_once_with(
            self.auth_token,
            self.organization_context,
            expected_query,
            expected_variables,
            'allProducts'
        )
        assert result == mock_get_all_paginated_results.return_value

    @patch("finite_state_sdk.get_all_paginated_results")
    def test_get_products_with_business_unit_id(self, mock_get_all_paginated_results):
        # Call the function with business_unit_id specified
        result = get_products(self.auth_token, self.organization_context, business_unit_id=self.business_unit_id)

        # Define expected query and variables
        expected_query = queries.GET_PRODUCTS['query']
        expected_variables = queries.GET_PRODUCTS['variables'](product_id=None, business_unit_id=self.business_unit_id)

        # Assertions
        mock_get_all_paginated_results.assert_called_once_with(
            self.auth_token,
            self.organization_context,
            expected_query,
            expected_variables,
            'allProducts'
        )
        assert result == mock_get_all_paginated_results.return_value

    @patch("finite_state_sdk.get_all_paginated_results")
    def test_get_products_with_product_id_and_business_unit_id(self, mock_get_all_paginated_results):
        # Call the function with both product_id and business_unit_id specified
        result = get_products(self.auth_token, self.organization_context, self.product_id, self.business_unit_id)

        # Define expected query and variables
        expected_query = queries.GET_PRODUCTS['query']
        expected_variables = queries.GET_PRODUCTS['variables'](product_id=self.product_id, business_unit_id=self.business_unit_id)

        # Assertions
        mock_get_all_paginated_results.assert_called_once_with(
            self.auth_token,
            self.organization_context,
            expected_query,
            expected_variables,
            'allProducts'
        )
        assert result == mock_get_all_paginated_results.return_value
