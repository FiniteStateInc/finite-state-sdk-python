# reads a CSV file and converts it to CycloneDX format
# Usage: python3 convert.py --input <input.csv>
# pip install cyclonedx-python-lib

import argparse
import csv
import datetime
import json
import sys
import uuid
from typing import TYPE_CHECKING

from cyclonedx.exception import MissingOptionalDependencyException
from cyclonedx.factory.license import LicenseFactory
from cyclonedx.model import ExternalReference, ExternalReferenceType, HashAlgorithm, HashType, OrganizationalEntity, XsUri
from cyclonedx.model.bom import Bom
from cyclonedx.model.component import Component, ComponentType
from cyclonedx.output import make_outputter
from cyclonedx.output.json import JsonV1Dot4
from cyclonedx.schema import OutputFormat, SchemaVersion
from cyclonedx.validation import make_schemabased_validator
from cyclonedx.validation.json import JsonStrictValidator
from packageurl import PackageURL

if TYPE_CHECKING:
    from cyclonedx.output.json import Json as JsonOutputter
    from cyclonedx.output.xml import Xml as XmlOutputter
    from cyclonedx.validation.xml import XmlValidator


lc_factory = LicenseFactory()


fields_type_1 = [
    'Component',
    'Version',
    'Latest Version',
    'Component Type',
    'License',
    'License Type',
    'Vulnerability Count',
    'Object Compilation Date',
    'Object',
    'Object full path',
    'Object SHA1',
    'Distribution package',
    'Missing exploit mitigations',
    'Version override type',
    'Licenses'
]

def map_v1(row, existing):
    csv_component = {
        'Author Name': 'Author',  # row['Author Name'].strip(),
        'Supplier Name': 'Supplier',  # row['Supplier Name'].strip(),
        'Component Name': row['Component'].strip(),
        'Version String': row['Version'].strip(),
        'Component Hash': row['Object SHA1'].strip(),
        'Unique Identifier': uuid.uuid1(),  # row['Unique Identifier'].strip(),
        'Relationship': 'Direct',  # row['Relationship'].strip(),
        'Package Download Location': 'None',  # row['Package Download Location'].strip(),
        'Timestamp': 'Object Compilation Date'  #row['Timestamp'].strip()
    }

    if {"name": csv_component['Component Name'], "version": csv_component['Version String']} in existing:
        return None

    component1 = Component(
        type=ComponentType.LIBRARY,
        name=csv_component['Component Name'],
        version=csv_component['Version String'],
        author=csv_component['Author Name'],
        hashes=[HashType(alg=HashAlgorithm.SHA_256, content=csv_component['Component Hash'])],
        supplier=OrganizationalEntity(
            name=csv_component['Supplier Name']
        ),
        bom_ref=csv_component['Unique Identifier'],
        #external_references=[ExternalReference(type=ExternalReferenceType.DISTRIBUTION, url=XsUri(csv_component['Package Download Location']))]
        #purl=PackageURL('generic', 'acme', 'some-component', '1.33.7-beta.1')
    )

    existing.append({"name": csv_component['Component Name'], "version": csv_component['Version String']})

    return component1


fields_type_2 = [
    "Component",
    "Version",
    "Latest version",
    "CVE",
    "Matching type",
    "CVSS",
    "CVE publication date",
    "Object compilation date",
    "Object",
    "Object full path",
    "Object SHA1",
    "CVSS3",
    "CVSS vector"
]


def map_v2(row, existing):
    csv_component = {
        'Author Name': 'Author',  # row['Author Name'].strip(),
        'Supplier Name': 'Supplier',  # row['Supplier Name'].strip(),
        'Component Name': row['Component'].strip(),
        'Version String': row['Version'].strip(),
        'Component Hash': row['Object SHA1'].strip(),
        'Unique Identifier': uuid.uuid1(),  # row['Unique Identifier'].strip(),
        'Relationship': 'Direct',  # row['Relationship'].strip(),
        'Package Download Location': 'None',  # row['Package Download Location'].strip(),
        'Timestamp': row['Object compilation date']  #row['Timestamp'].strip()
    }

    if {"name": csv_component['Component Name'], "version": csv_component['Version String']} in existing:
        return None

    component = Component(
        type=ComponentType.LIBRARY,
        name=csv_component['Component Name'],
        version=csv_component['Version String'],
        author=csv_component['Author Name'],
        hashes=[HashType(alg=HashAlgorithm.SHA_256, content=csv_component['Component Hash'])],
        supplier=OrganizationalEntity(
            name=csv_component['Supplier Name']
        ),
        bom_ref=csv_component['Unique Identifier'],
        #external_references=[ExternalReference(type=ExternalReferenceType.DISTRIBUTION, url=XsUri(csv_component['Package Download Location']))]
        #purl=PackageURL('generic', 'acme', 'some-component', '1.33.7-beta.1')
    )

    existing.append({"name": csv_component['Component Name'], "version": csv_component['Version String']})

    return component


fields_type_3 = [
    "Component",
    "Version",
    "Latest version",
    "CVE",
    "Matching type",
    "CVSS",
    "CVE publication date",
    "Object compilation date",
    "Object",
    "Object full path",
    "Object SHA1",
    "CVSS3",
    "CVSS vector (v2)",
    "CVSS vector (v3)",
    "Summary",
    "Distribution package",
    "CVSS (Distribution)",
    "CVSS3 (Distribution)",
    "Triage vectors",
    "Unresolving triage vectors",
    "Note type",
    "Note reason",
    "Vulnerability URL",
    "Missing exploit mitigations",
    "BDSA"
]

def map_v3(row, existing):
    csv_component = {
        'Author Name': 'Author',  # row['Author Name'].strip(),
        'Supplier Name': 'Supplier',  # row['Supplier Name'].strip(),
        'Component Name': row['Component'].strip(),
        'Version String': row['Version'].strip(),
        'Component Hash': row['Object SHA1'].strip(),
        'Unique Identifier': uuid.uuid1(),  # row['Unique Identifier'].strip(),
        'Relationship': 'Direct',  # row['Relationship'].strip(),
        'Package Download Location': 'None',  # row['Package Download Location'].strip(),
        'Timestamp': row['Object compilation date']  #row['Timestamp'].strip()
    }

    if {"name": csv_component['Component Name'], "version": csv_component['Version String']} in existing:
        return None

    component = Component(
        type=ComponentType.LIBRARY,
        name=csv_component['Component Name'],
        version=csv_component['Version String'],
        author=csv_component['Author Name'],
        hashes=[HashType(alg=HashAlgorithm.SHA_256, content=csv_component['Component Hash'])],
        supplier=OrganizationalEntity(
            name=csv_component['Supplier Name']
        ),
        bom_ref=csv_component['Unique Identifier'],
        #external_references=[ExternalReference(type=ExternalReferenceType.DISTRIBUTION, url=XsUri(csv_component['Package Download Location']))]
        #purl=PackageURL('generic', 'acme', 'some-component', '1.33.7-beta.1')
    )

    existing.append({"name": csv_component['Component Name'], "version": csv_component['Version String']})

    return component


fields_type_4 = [
    "Component",
    "Version",
    "Latest version",
    "Component type",
    "License",
    "License type",
    "Vulnerability count",
    "Object compilation date",
    "Object",
    "Object full path",
    "Object SHA1",
    "Distribution package",
    "Missing exploit mitigations",
    "Version override type",
    "Licenses"
]


def map_v4(row, existing):
    csv_component = {
        'Author Name': 'Author',  # row['Author Name'].strip(),
        'Supplier Name': 'Supplier',  # row['Supplier Name'].strip(),
        'Component Name': row['Component'].strip(),
        'Version String': row['Version'].strip(),
        'Component Hash': row['Object SHA1'].strip(),
        'Unique Identifier': uuid.uuid1(),  # row['Unique Identifier'].strip(),
        'Relationship': 'Direct',  # row['Relationship'].strip(),
        'Package Download Location': 'None',  # row['Package Download Location'].strip(),
        'Timestamp': row['Object compilation date']  #row['Timestamp'].strip()
    }

    if {"name": csv_component['Component Name'], "version": csv_component['Version String']} in existing:
        return None

    component = Component(
        type=ComponentType.LIBRARY,
        name=csv_component['Component Name'],
        version=csv_component['Version String'],
        author=csv_component['Author Name'],
        hashes=[HashType(alg=HashAlgorithm.SHA_256, content=csv_component['Component Hash'])],
        supplier=OrganizationalEntity(
            name=csv_component['Supplier Name']
        ),
        bom_ref=csv_component['Unique Identifier']
    )

    existing.append({"name": csv_component['Component Name'], "version": csv_component['Version String']})

    return component

fields_type_5 = [
    "Library_ldd",
    "Library_realpath",
    "PackageName",
    "PackageVersion",
    "PackageSource",
    "PackageHomepage"
]


def map_v5(row, existing):
    csv_component = {
        'Author Name': 'NOASSERTION',  # row['Author Name'].strip(),
        'Supplier Name': 'NOASSERTION',  # row['Supplier Name'].strip(),
        'Component Name': row['PackageName'].strip(),
        'Version String': row['PackageVersion'].strip(),
        'Component Hash': "NOASSERTION",
        'Unique Identifier': uuid.uuid1(),  # row['Unique Identifier'].strip(),
        'Relationship': "NOASSERTION",  # row['Relationship'].strip(),
        'Package Download Location': row['PackageHomepage'].strip(),  # row['Package Download Location'].strip(),
    }

    if {"name": csv_component['Component Name'], "version": csv_component['Version String']} in existing:
        return None

    component = Component(
        type=ComponentType.LIBRARY,
        name=csv_component['Component Name'],
        version=csv_component['Version String'],
        author=csv_component['Author Name'],
        #hashes=[HashType(alg=HashAlgorithm.SHA_256, content=csv_component['Component Hash'])],
        supplier=OrganizationalEntity(
            name=csv_component['Supplier Name']
        ),
        bom_ref=csv_component['Unique Identifier'],
        #external_references=[ExternalReference(type=ExternalReferenceType.DISTRIBUTION, url=XsUri(csv_component['Package Download Location']))]
        #purl=PackageURL('generic', 'acme', 'some-component', '1.33.7-beta.1')
    )

    existing.append({"name": csv_component['Component Name'], "version": csv_component['Version String']})

    return component


def main():
    parser = argparse.ArgumentParser(description='Converts a CSV file to CycloneDX format. Supports multiple example CSV formats')
    parser.add_argument('--input', type=str, help='The input CSV file', required=True)
    args = parser.parse_args()

    existing = []
    components = []
    with open(args.input, newline='') as csvfile:
        # get the first line of the file, and figure out which type of CSV file it is
        first_line = csvfile.readline().strip().replace('"', '')
        if first_line == ','.join(fields_type_1):
            print('Detected Type 1')
            fieldnames = fields_type_1
            mapper = map_v1
            print(f'Fieldnames: {fieldnames}')
            print(f'First line: {first_line}')
        elif first_line == ','.join(fields_type_2):
            print('Detected Type 2')
            fieldnames = fields_type_2
            mapper = map_v2
        elif first_line == ','.join(fields_type_3):
            print('Detected Type 3')
            fieldnames = fields_type_3
            mapper = map_v3
        elif first_line == ','.join(fields_type_4):
            print('Detected Type 4')
            fieldnames = fields_type_4
            mapper = map_v4
        elif first_line == ','.join(fields_type_5):
            print('Detected Type 5')
            fieldnames = fields_type_5
            mapper = map_v5
        else:
            print('Unknown CSV format')
            print(first_line)
            print(','.join(fields_type_3))
            sys.exit(1)

        print(f'Fieldnames: {fieldnames}')
        reader = csv.DictReader(csvfile, fieldnames=fieldnames)

        for row in reader:
            component = mapper(row, existing)
            if component is not None:
                components.append(component)

    # region build the BOM
    bom = Bom()
    bom.metadata.component = root_component = Component(
        name='File',
        type=ComponentType.APPLICATION,
        bom_ref='File-1.0.0',
    )

    for component in components:
        bom.components.add(component)
        #bom.register_dependency(root_component, [component])


    # endregion build the BOM

    """demo with explicit instructions for SchemaVersion, outputter and validator"""

    my_json_outputter: 'JsonOutputter' = JsonV1Dot4(bom)
    serialized_json = my_json_outputter.output_as_string(indent=2)

    my_json_validator = JsonStrictValidator(SchemaVersion.V1_4)
    try:
        validation_errors = my_json_validator.validate_str(serialized_json)
        if validation_errors:
            print('JSON invalid', 'ValidationError:', repr(validation_errors), sep='\n', file=sys.stderr)
            sys.exit(2)
        #print('JSON valid')
    except MissingOptionalDependencyException as error:
        #print('JSON-validation was skipped due to', error)
        pass

    # output to file
    output_filename = f'{args.input}.cyclonedx.json'
    with open(output_filename, "w") as f:
        f.write(serialized_json)
        print(f'Wrote {output_filename}')

main()

