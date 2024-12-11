from gql import gql
from graphql.language.ast import OperationDefinitionNode, OperationType


class BreakoutException(Exception):
    """Exception raised for errors in the BreakoutException."""

    pass


def is_not_breakout_exception(exception):
    """Check if the exception is not a BreakoutException."""
    return not isinstance(exception, BreakoutException)


def is_mutation(query_string):
    """
    Check if the provided GraphQL query string contains any mutations.

    Args:
        query_string (str): The GraphQL query string.

    Returns:
        bool: True if there is a mutation, False otherwise.
    """
    operation_types = determine_operation_types(query_string)
    return OperationType.MUTATION in operation_types


def determine_operation_types(query_string):
    # Parse the query string
    query_doc = gql(query_string)
    operation_types = []

    # Check the type of the first operation in the document
    for definition in query_doc.definitions:
        if isinstance(definition, OperationDefinitionNode):
            operation_types.append(definition.operation)

    return operation_types


# @retry(stop=stop_after_attempt(2), wait=wait_fixed(2), retry=retry_if_exception(is_not_breakout_exception))
# def send_graphql_query(token, organization_context, query, variables=None):
#     print(f"====Hello from send_graphql_query! {query}")
#     """
#     Send a GraphQL query to the API

#     Args:
#         token (str):
#             Auth token. This is the token returned by get_auth_token(). Just the token, do not include "Bearer" in this string, that is handled inside the method.
#         organization_context (str):
#             Organization context. This is provided by the Finite State API management. It looks like "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx".
#         query (str):
#             The GraphQL query string
#         variables (dict, optional):
#             Variables to be used in the GraphQL query, by default None

#     Raises:
#         Exception: If the response status code is not 200

#     Returns:
#         dict: Response JSON
#     """
#     headers = {
#         "Content-Type": "application/json",
#         "Authorization": f"Bearer {token}",
#         "Organization-Context": organization_context,
#     }
#     data = {"query": query, "variables": variables}

#     response = requests.post(API_URL, headers=headers, json=data)
#     print(f"Response: {response.text}")
#     if response.status_code == 200:
#         thejson = response.json()

#         if "errors" in thejson:
#             print(f"GRAPHQL Errors: {thejson['errors']}")
#             # Raise a BreakoutException for GraphQL errors
#             raise BreakoutException(f"Error: {thejson['errors']}")

#         return thejson
#     else:
#         is_mutation_operation = is_mutation(query)
#         print(f"--Is Mutation Operation: {is_mutation_operation}")
#         if is_mutation_operation:
#             raise BreakoutException(f"Error: {response.status_code} - {response.text}")
#         else:
#             print("---RETRYING")
#             raise Exception(f"Error: {response.status_code} - {response.text}")
