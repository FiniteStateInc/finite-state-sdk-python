import os
import pytest
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'examples'))
from get_all_components_metadata import authenticate
from get_all_components_metadata import apply_filters
from get_all_components_metadata import export_to_csv, export_to_json
import tempfile
import csv
import json

def test_authenticate_with_valid_secrets():
    secrets_file = os.path.join(os.path.dirname(__file__), '../examples/.secrets_scd')
    assert os.path.exists(secrets_file), f"Secrets file not found: {secrets_file}"
    token, org_context = authenticate(secrets_file)
    assert token, "Authentication token should not be empty"
    assert org_context, "Organization context should not be empty"

def test_apply_filters_status_and_type():
    # Components with filtered status or type should be excluded
    components = [
        {'id': 1, 'currentStatus': {'status': 'REVIEWED_FALSE_POSITIVE'}, 'type': 'library', 'absoluteRiskScore': 5.0},
        {'id': 2, 'currentStatus': {'status': 'EXCLUDED'}, 'type': 'library', 'absoluteRiskScore': 5.0},
        {'id': 3, 'currentStatus': {'status': 'ACTIVE'}, 'type': 'file', 'absoluteRiskScore': 5.0},
        {'id': 4, 'currentStatus': {'status': 'ACTIVE'}, 'type': 'library', 'absoluteRiskScore': 5.0},
    ]
    filters = {}
    filtered = apply_filters(components, filters)
    # Only the last component should remain
    assert len(filtered) == 1
    assert filtered[0]['id'] == 4

def test_apply_filters_component_type():
    # Only components of the specified type should remain
    components = [
        {'id': 1, 'currentStatus': {'status': 'ACTIVE'}, 'type': 'library', 'absoluteRiskScore': 5.0},
        {'id': 2, 'currentStatus': {'status': 'ACTIVE'}, 'type': 'application', 'absoluteRiskScore': 5.0},
    ]
    filters = {'component_type': 'library'}
    filtered = apply_filters(components, filters)
    assert len(filtered) == 1
    assert filtered[0]['type'] == 'library'

def test_apply_filters_min_risk_score():
    # Only components with risk score >= min_risk_score should remain
    components = [
        {'id': 1, 'currentStatus': {'status': 'ACTIVE'}, 'type': 'library', 'absoluteRiskScore': 2.0},
        {'id': 2, 'currentStatus': {'status': 'ACTIVE'}, 'type': 'library', 'absoluteRiskScore': 5.0},
    ]
    filters = {'min_risk_score': 3.0}
    filtered = apply_filters(components, filters)
    assert len(filtered) == 1
    assert filtered[0]['absoluteRiskScore'] == 5.0

def test_export_to_csv_headers_and_data():
    # Prepare mock components
    components = [
        {
            'assetVersion': {
                'asset': {'id': 'A1', 'name': 'ArtifactX'},
                'id': 'V1',
                'name': 'VersionX',
            },
            'name': 'ComponentA',
            'version': '1.2.3',
            'summaryDescription': 'desc',
            'detailedDescription': 'details',
            'supportEol': True,
            'properties': [
                {'key': 'finitestate:sbom:component_id', 'value': 'CID123'},
                {'key': 'custom', 'value': 'customval'}
            ]
        }
    ]
    with tempfile.NamedTemporaryFile('r+', newline='', encoding='utf-8', delete=False) as tmp:
        export_to_csv(components, tmp.name)
        tmp.seek(0)
        reader = csv.DictReader(tmp)
        headers = reader.fieldnames
        row = next(reader)
    # Check key headers
    assert 'Artifact ID' in headers
    assert 'Artifact Name' in headers
    assert 'Version ID' in headers
    assert 'Version Name' in headers
    assert 'name' in headers
    assert 'version' in headers
    assert row['Artifact ID'] == 'A1'
    assert row['Artifact Name'] == 'ArtifactX'
    assert row['Version ID'] == 'V1'
    assert row['Version Name'] == 'VersionX'
    assert row['name'] == 'ComponentA'
    assert row['version'] == '1.2.3'
    assert row['property:finitestate:sbom:component_id'] == 'CID123'
    assert 'custom_properties' in headers
    assert 'custom=customval' in row['custom_properties']

def test_export_to_json_metadata_and_components():
    # Prepare mock components
    components = [
        {'name': 'ComponentA', 'version': '1.2.3'},
        {'name': 'ComponentB', 'version': '2.0.0'}
    ]
    with tempfile.NamedTemporaryFile('r+', encoding='utf-8', delete=False) as tmp:
        export_to_json(components, tmp.name, summary={'foo': 'bar'})
        tmp.seek(0)
        data = json.load(tmp)
    assert 'metadata' in data
    assert 'components' in data
    assert data['metadata']['component_count'] == 2
    assert data['metadata']['foo'] == 'bar'
    assert data['components'][0]['name'] == 'ComponentA'
    assert data['components'][1]['version'] == '2.0.0' 