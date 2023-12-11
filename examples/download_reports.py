import datetime
import finite_state_sdk
import requests


def custom_download_report(token, organization_context, report_type="CSV", report_subtype="ALL_FINDINGS", asset_version_id=None, output_filename=None):
    """
    Demonstration of a method for getting a download URL.
    Downloads a report from the Finite State Platform and saves it to the specified output_filename.
    You could build your own method to do something else with the URL, or you can use the built-in finite_state_sdk.download_asset_version_report() method.
    :param token: Finite State API token
    :param organization_context: Finite State API organization context
    :param report_type: The type of report to download. Valid values are "CSV" and "PDF"
    :param report_subtype: The subtype of report to download. Valid values are "ALL_FINDINGS", "ALL_COMPONENTS", "EXPLOIT_INTELLIGENCE", and "RISK_SUMMARY". See API documentation for details.
    :param asset_version_id: The asset version ID to download the SBOM for
    :param output_filename: The filename to save the SBOM to
    """
    url = finite_state_sdk.generate_report_download_url(token, organization_context, asset_version_id=asset_version_id, report_type=report_type, report_subtype=report_subtype, verbose=True) -> str:

    # Send an HTTP GET request to the URL
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Open a local file in binary write mode and write the content to it
        print("File downloaded successfully.")
        with open(output_filename, 'wb') as file:
            file.write(response.content)
            print(f'Wrote file to {output_filename}')
    else:
        print("Failed to download the file. Status code:", response.status_code)


def example_download_reports(token, organization_context):
    # Download Reports for an asset version using custom method
    asset_version_id = '123456789'
    custom_download_report(token, organization_context, report_type="CSV", report_subttype="ALL_FINDINGS", asset_version_id=asset_version_id, output_filename=f'{asset_version_id}-all_findings.csv')

    # Download Reports for an asset version using built-in SDK functions
    downloads_folder = "downloads"
    dt = datetime.datetime.now().strftime("%Y-%m-%d-%H%M")

    # Download a CSV report of all findings for an asset version
    finite_state_sdk.download_asset_version_report(token, organization_context, report_type="CSV", report_subtype="ALL_FINDINGS", asset_version_id='123456789', output_filename=f"{downloads_folder}/{dt}-artifact_version-all_findings.csv", verbose=True)
    # Download a CSV report of all components for an asset version
    finite_state_sdk.download_asset_version_report(token, organization_context, report_type="CSV", report_subtype="ALL_COMPONENTS", asset_version_id='123456789', output_filename=f"{downloads_folder}/{dt}-artifact_version-all_components.csv", verbose=True)
    # Download a CSV report of all exploit intelligence for an asset version
    finite_state_sdk.download_asset_version_report(token, organization_context, report_type="CSV", report_subtype="EXPLOIT_INTELLIGENCE", asset_version_id='123456789', output_filename=f"{downloads_folder}/{dt}-artifact_version-exploit_intelligence.csv", verbose=True)
    # Download a PDF report of the risk summary for an asset version
    finite_state_sdk.download_asset_version_report(token, organization_context, report_type="PDF", report_subtype="RISK_SUMMARY", asset_version_id='123456789', output_filename=f"{downloads_folder}/{dt}-artifact_version-risk_summary.pdf", verbose=True)

    # Download Reports for a product

    # Download a CSV report of all findings for a product
    finite_state_sdk.download_product_report(token, organization_context, report_type="CSV", report_subtype="ALL_FINDINGS", product_id='123456789', output_filename=f"{downloads_folder}/{dt}-product-all_findings.csv", verbose=True)


