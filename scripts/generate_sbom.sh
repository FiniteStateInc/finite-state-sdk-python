#!/bin/bash

if [ -e "sbom/cyclonedx.sbom.json.unformatted" ]; then
    rm sbom/cyclonedx.sbom.json.unformatted
fi
poetry run cyclonedx-py -r --format json -o sbom/cyclonedx.sbom.json.unformatted
cat sbom/cyclonedx.sbom.json.unformatted | jq '.' > sbom/cyclonedx.sbom.json
rm sbom/cyclonedx.sbom.json.unformatted
