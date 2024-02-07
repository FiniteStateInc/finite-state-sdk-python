import argparse
import datetime
import os
from dotenv import load_dotenv

import finite_state_sdk


def main():
    dt = datetime.datetime.now()
    dt_str = dt.strftime("%Y-%m-%d-%H%M")

    parser = argparse.ArgumentParser(description='Update Finding Statuses')
    parser.add_argument('--secrets-file', type=str, help='Path to the secrets file', required=True)

    args = parser.parse_args()

    load_dotenv(args.secrets_file, override=True)

    # get CLIENT_ID and CLIENT_SECRET from env
    CLIENT_ID = os.environ.get("CLIENT_ID")
    CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
    ORGANIZATION_CONTEXT = os.environ.get("ORGANIZATION_CONTEXT")

    # Get an auth token - this is a bearer token that you will use for all subsequent requests
    # The token is valid for 24 hours
    token = finite_state_sdk.get_auth_token(CLIENT_ID, CLIENT_SECRET)

    # these are the finding IDs to update - you can specify one, or multiple
    # if specifying multiple, they will all have the same resolution and comment
    finding_ids = ['123456789', '234567891']  # replace with your finding IDs


    # -------- NOT AFFECTED EXAMPLE --------

    # The status to apply to the Findings
    # These statuses align with the VEX resolution statuses: https://www.cisa.gov/sites/default/files/publications/VEX_Use_Cases_April2022.pdf
    # For details about avialable statuses, see: https://docs.finitestate.io/types/finding-status-option
    new_status = "NOT_AFFECTED"

    # Valid Justifications for NOT_AFFECTED status, describing why the vulnerability is not present or not a concern:
    # ["COMPONENT_NOT_PRESENT", "INLINE_MITIGATIONS_ALREADY_EXIST", "VULNERABLE_CODE_CANNOT_BE_CONTROLLED_BY_ADVERSARY", "VULNERABLE_CODE_NOT_IN_EXECUTE_PATH", "VULNERABLE_CODE_NOT_PRESENT"]
    # For details, see: https://docs.finitestate.io/types/finding-status-justification-enum
    justification = "COMPONENT_NOT_PRESENT"

    # The comment will be applied to the Finding resolution
    comment = "Updating status to NOT_AFFECTED with justification: COMPONENT_NOT_PRESENT for finding_ids: {finding_ids}")

    # For more info see: https://docs.finitestate.io/mutations/update-findings-statuses
    gql_response = finite_state_sdk.update_findings_status(token, ORGANIZATION_CONTEXT, status=new_status, justification=justification, comment=comment)

    updated_finding_ids = gql_response["data"]["updateFindingsStatuses"]["ids"]
    print(f'Updated {len(updated_finding_ids)} findings')


    # -------- AFFECTED EXAMPLE --------

    finding_ids = ['345678912', '456789123']  # replace with your finding IDs

    # The status to apply to the Findings
    new_status = "AFFECTED"

    # Valid Vendor responses for AFFECTED status, describing what the vendor will do about the vulnerability:
    #["CANNOT_FIX", "ROLLBACK_REQUIRED", "UPDATE_REQUIRED", "WILL_NOT_FIX", "WORKAROUND_AVAILABLE"]
    # For details, see: https://docs.finitestate.io/types/finding-status-response-enum
    response = "CANNOT_FIX"

    # The comment will be applied to the Finding resolution
    comment = "Updating status to AFFECTED with response: CANNOT_FIX for finding_ids: {finding_ids}")

    # For more info see: https://docs.finitestate.io/mutations/update-findings-statuses
    gql_response = finite_state_sdk.update_findings_status(token, ORGANIZATION_CONTEXT, status=new_status, response=response, comment=comment)

    updated_finding_ids = gql_response["data"]["updateFindingsStatuses"]["ids"]
    print(f'Updated {len(updated_finding_ids)} findings')


if __name__ == "__main__":
    main()
