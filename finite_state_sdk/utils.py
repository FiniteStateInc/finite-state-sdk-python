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
