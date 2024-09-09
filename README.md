# Compliance testing to MIM7 - Places

_MIM7 - Places_ is one of the Minimal Interoperability Mechanisms (MIMs) developed by the [Open & Agile Smart Cities](https://oascities.org/) network under the [Living-in.EU!](https://living-in.eu/) initiative, which aims at facilitating seamless and interoperable sharing and re-use of digital, data-driven solutions in cities and regions across Europe and beyond.

The latest version of the MIMs is available [here](https://oasc.gitbook.io/mims-2024); the corresponding latest version of _MIM7 - Places_ is maintained [here](https://oasc.gitbook.io/mims-2024/mims/oasc-mim7-places).

This repository provides tests written in Python to check compliance to the requirements of _MIM7 - Places_.

For each Requirement, the repository also provides the Python code to generate an API using FastAPI, python 3.12.5, which exposes the tests.

## Local Development

Necessary to have pyenv installed and running local virtualenv.

Install pyenv and generic info: [Intro into pyenv](https://realpython.com/intro-to-pyenv/)

Python version install:

```bash
cd .
pyenv install 3.12.5
```

Set virtual env:

```bash
pyenv virtualenv 3.12.5 OASC-NIM7-compliance-2024
pyenv local OASC-NIM7-compliance-2024
pyenv shell OASC-NIM7-compliance-2024
```

## Env variables

We have `.env` implemented for debug only. An `.env` file will be used to set debugging level:

```bash
cd API
touch .env # Generic env variables
echo "API_LOG_LEVEL=DEBUG" >> .env
```

See file [env.example](./API/env.example)

## Debug levels

Implementing default Python debug levels using env variable with the following options:

`API_LOG_LEVEL -> ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]`

If `API_LOG_LEVEL`  is not set, then it will default to "INFO"

## Running docker build

For docker deployment:

```bash
cd .
docker build --no-cache -t oasc-mim7-api:0.0.1 .
docker run -e "API_LOG_LEVEL=DEBUG" -p 8000:8000 oasc-mim7-api:0.0.1
```

To set ports check the Dockerfile

## API docs

FastAPI has internal implementations of Open API docs and Redocs, in the following links:

- Open API docs [http://localhost:8000/docs](http://localhost:8000/docs)
- Redocs [http://localhost:8000/redocs](http://localhost:8000/redocs)

## API testing

Basic testing can be done on the Open API docs or Redocs GUI, but also with curl on the terminal

`r1` end point test urls:

`WFS 2.0.0` compliant:

```bash
cd .
curl -X 'GET' \
  'http://localhost:8000/r1?url=https%3A%2F%2Fgeoserver.epsilon-italia.it%2Fgeoserver%2FLU_sample%2Fows' \
  -H 'accept: application/json'

{
  "service_url": "https://geoserver.epsilon-italia.it/geoserver/LU_sample/ows",
  "status": "compliant",
  "details": "The service is a valid MIM-7 OGC WFS service."
}
```

`OGC API features` compliant:

```bash
cd .
curl -X 'GET' \
  'http://localhost:8000/r1?url=https%3A%2F%2Fdemo.pygeoapi.io%2Fstable%2F' \
  -H 'accept: application/json'

{
  "service_url": "https://demo.pygeoapi.io/stable/",
  "status": "compliant",
  "details": "The service is a valid MIM-7 OGC API Features service."
}
```

Non compliant service:

```bash
cd .
curl -X 'GET' \
  'http://localhost:8000/r1?url=www.google.com' \
  -H 'accept: application/json'

{
  "detail": {
    "service_url": "www.google.com",
    "status": "error",
    "details": "Unable to contact the service. Check the URL."
  }
}

For gepackage testing:

```bash
cd .
curl -X POST "http://127.0.0.1:8000/r2" \
-H "accept: application/json" \
-H "Content-Type: multipart/form-data" \ 
-F "file=@./API/tests/example.gpkg"

{"layer_name":"point1","contains_geospatial_data":true,"identifiers_unique":true,"identifiers_persistent":true,"message":null}
```
