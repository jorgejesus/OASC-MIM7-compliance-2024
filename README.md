# Compliance testing to MIM7 - Places

_MIM7 - Places_ is one of the Minimal Interoperability Mechanisms (MIMs) developed by the [Open & Agile Smart Cities](https://oascities.org/) network under the [Living-in.EU!](https://living-in.eu/) initiative, which aims at facilitating seamless and interoperable sharing and re-use of digital, data-driven solutions in cities and regions across Europe and beyond.

The latest version of the MIMs is available [here](https://oasc.gitbook.io/mims-2024); the corresponding latest version of _MIM7 - Places_ is maintained [here](https://oasc.gitbook.io/mims-2024/mims/oasc-mim7-places).

This repository provides tests written in Python to check compliance to the requirements of _MIM7 - Places_. Currently, the following tests are available:

- **Requirement R1**: tests to check whether geospatial data are exposed through OGC WFS and OGC API - Features.
- **Requirements R2, R3, R5**: tests to check whether a geospatial dataset is encoded according to the GeoPackage specifications and has objects with unique and persistent identifiers.

For each Requirement, the repository also provides the Python code to generate an API using Flask, which exposes the tests.
