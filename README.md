# openstreetmap-serverless-functions
**[working-draft] Collection of serverless functions ([OpenFaas spec](https://www.openfaas.com/)) for use with OpenStreetMap™.**

[![OpenFaas](img/openfaas-whale.png)](https://www.openfaas.com/)

<!--
- Examples
  - https://github.com/openfaas/store-functions/blob/master/stack.yml
  - https://github.com/faas-and-furious/youtube-dl/blob/master/entry.sh
-->

## Functions

### api-rdf

> TODO: maybe glue https://github.com/hugapi/hug/tree/develop/docker plus https://github.com/EticaAI/openstreetmap-semantic-conventions-2023/blob/main/poc/osmapi2rdfproxy.py ?

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