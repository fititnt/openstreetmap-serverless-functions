# openstreetmap-serverless-functions
**[working-draft] Collection of serverless functions ([OpenFaas spec](https://www.openfaas.com/)) for use with OpenStreetMap™.**

[![OpenFaas](img/openfaas-whale.png)](https://www.openfaas.com/)

<!--
- Examples
  - https://github.com/openfaas/store-functions/blob/master/stack.yml
  - https://github.com/faas-and-furious/youtube-dl/blob/master/entry.sh
-->

## Functions

### api-proxy

- **Environment Variables**
  - `OSM_API_DE_FACTO`: `https://www.openstreetmap.org/api/0.6`
  - `CACHE_DRIVER`: `sqlite`
  - `CACHE_TTL`: `3600`

<!--

## rebuild drill
cd function/
cp -r $(pwd)/* ~/Downloads/docker-build-dir
cd ~/Downloads/docker-build-dir

# docker build -t ghcr.io/fititnt/api-proxy ./api-proxy
faas-cli build -f ./api-proxy-local.yml

docker run --name api-proxy --publish 8080:8080 -d ghcr.io/fititnt/api-proxy && docker logs --follow api-proxy
docker container stop api-proxy && docker container rm api-proxy

docker container start --interactive api-proxy
docker container start --interactive 04d37527c20728f4aab1dff6b1a02017bc9e3074fffe116d6caee76d8f57a83b
docker logs --follow api-proxy

-->


### api-rdf

<!-- > TODO: maybe glue https://github.com/hugapi/hug/tree/develop/docker plus https://github.com/EticaAI/openstreetmap-semantic-conventions-2023/blob/main/poc/osmapi2rdfproxy.py ? -->

- **Environment Variables**
  - `OSM_API_DE_FACTO`: `https://www.openstreetmap.org/api/0.6`
  - `CACHE_DRIVER`: `sqlite`
  - `CACHE_TTL`: `3600`

<!--

## rebuild drill
cd function/
cp -r $(pwd)/* ~/Downloads/docker-build-dir
cd ~/Downloads/docker-build-dir

# docker build -t ghcr.io/fititnt/api-rdf ./api-rdf
faas-cli build -f ./api-rdf-local.yml

# faas-cli publish -f ./api-rdf-local.yml
faas-cli deploy -f ./api-rdf-local.yml

docker tag api-proxy:latest ghcr.io/fititnt/api-proxy:latest
docker push ghcr.io/fititnt/api-proxy:latest

docker run --name api-rdf --publish 8080:8080 -d ghcr.io/fititnt/api-rdf && docker logs --follow api-rdf
docker container stop api-rdf && docker container rm api-rdf

-->

### curl

> OpenFaaS test function. Not related to OpenStreetMap. Ignore for now.

### sentimentanalysis

> OpenFaaS test function. Not related to OpenStreetMap. Ignore for now.

## Guides

### Developers of functions

> TODO: draft this.

### Sysadmins

> This is a draft. Ignore for now.

```
export OPENFAAS_URL=https://osm-faas.etica.ai/
export OPENFAAS_USER=admin

# (...)

# docker build -t fititnt/curl function/curl/
```

## Disclaimers
<!--
TODO see https://wiki.osmfoundation.org/wiki/Trademark_Policy
-->

OpenStreetMap™ is a trademark of the OpenStreetMap Foundation, and is used with their permission.
This project is not endorsed by or affiliated with the OpenStreetMap Foundation. (via [OSMF Trademark_Policy](https://wiki.osmfoundation.org/wiki/Trademark_Policy))

## License


[![Public Domain](https://i.creativecommons.org/p/zero/1.0/88x31.png)](LICENSE)

Public domain