import finite_state_sdk
import requests


def custom_download_sbom(token, organization_context, sbom_type="CYCLONEDX", sbom_subtype="SBOM_ONLY", asset_version_id=None, output_filename=None):
    """
    Demonstration of a method for getting a download URL. Downloads an SBOM from the Finite State Platform and saves it to the specified output_filename.
    You could build your own method to do something else with the URL, or you can use the built-in finite_state_sdk.download_sbom() method.
    :param token: Finite State API token
    :param organization_context: Finite State API organization context
    :param sbom_type: The type of SBOM to download. Valid values are "CYCLONEDX" and "SPDX"
    :param sbom_subtype: The subtype of SBOM to download. Valid values are "SBOM_ONLY", "SBOM_WITH_VDR", and "VDR_ONLY"
    :param asset_version_id: The asset version ID to download the SBOM for
    :param output_filename: The filename to save the SBOM to
    """
    url = finite_state_sdk.generate_sbom_download_url(token, organization_context, sbom_type=sbom_type, sbom_subtype=sbom_subtype, asset_version_id=asset_version_id)

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


def example_download_sboms(token, organization_context):
    custom_download_sbom(token, organization_context, sbom_type="CYCLONEDX", sbom_subtype="SBOM_ONLY", asset_version_id='123456789', output_filename='sbom.cyclonedx.sbom_only.json')
    custom_download_sbom(token, organization_context, sbom_type="CYCLONEDX", sbom_subtype="SBOM_WITH_VDR", asset_version_id='123456789', output_filename='sbom.cyclonedx.sbom_with_vdr.json')
    custom_download_sbom(token, organization_context, sbom_type="CYCLONEDX", sbom_subtype="VDR_ONLY", asset_version_id='123456789', output_filename='sbom.cyclonedx.vdr_only.json')
    custom_download_sbom(token, organization_context, sbom_type="SPDX", sbom_subtype="SBOM_ONLY", asset_version_id='123456789', output_filename='sbom.spdx.sbom_only.json')

    finite_state_sdk.download_sbom(token, organization_context, sbom_type="CYCLONEDX", sbom_subtype="SBOM_ONLY", asset_version_id='123456789', output_filename='sbom.cyclonedx.sbom_only.json', verbose=True)

