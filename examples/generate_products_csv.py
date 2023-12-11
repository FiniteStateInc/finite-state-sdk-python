# queries the API using the SDK to generate a CSV report for all Products in the Organization
import argparse
import datetime
import json
import os
from dotenv import load_dotenv

import sys
sys.path.append('..')
import finite_state_sdk

def main():
    dt = datetime.datetime.now()
    dt_str = dt.strftime("%Y-%m-%d-%H%M")

    parser = argparse.ArgumentParser(description='Generate an CSV Products Report')
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

    products = finite_state_sdk.get_all_products(token, ORGANIZATION_CONTEXT)
    product_data = []

    for product in products:
        counts = {
            'CRITICAL': 0,
            'HIGH': 0,
            'MEDIUM': 0,
            'LOW': 0
        }

        product_name = product['name']

        # get the default version for the assets in the product
        for asset_version in product['assets']:
            asset_version_id = str(asset_version['id'])

            # get the count of findings for each severity
            severities = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
            for severity in severities:
                # do this because we can't in-line the findings meta query via the API, yet, and it requires several calls to get the counts
                count = finite_state_sdk.get_findings(token, ORGANIZATION_CONTEXT, asset_version_id=asset_version_id, severity=severity, count=True)['count']
                counts[severity] += count

        product_data.append({
            'product_name': product_name,
            'relative_risk_score': product['relativeRiskScore'] if product['relativeRiskScore'] else 0,
            'findings_critical': counts['CRITICAL'],
            'findings_high': counts['HIGH'],
            'findings_medium': counts['MEDIUM'],
            'findings_low': counts['LOW'],
            'artifact_count': len(product['assets']),
            'business_unit': product['group']['name'],
            'creator': f'{product["createdBy"]["email"]} {product["createdAt"]}'
        })

    # sort the product data by relative risk score
    product_data = sorted(product_data, key=lambda k: k['relative_risk_score'], reverse=True)

    # write to a csv file
    filename = f'{dt_str}-product-report.csv'
    with open(filename, 'w') as f:
        f.write('product_name,relative_risk_score,findings_critical,findings_high,findings_medium,findings_low,artifact_count,business_unit,creator\n')
        for product in product_data:
            # format the relative risk score float to a string with 1 decimal places
            product['relative_risk_score'] = f'{product["relative_risk_score"]:.1f}'
            f.write(f"{product['product_name']},{product['relative_risk_score']},{product['findings_critical']},{product['findings_high']},{product['findings_medium']},{product['findings_low']},{product['artifact_count']},{product['business_unit']},{product['creator']}\n")
        print(f'Wrote product report to {filename}')


main()
