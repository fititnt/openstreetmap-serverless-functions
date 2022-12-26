# apps-example/README.md

> https://github.com/openfaas/python-flask-template


```bash
faas-cli template store pull python3-flask

# faas-cli new osm-api-proxy --lang python3-http
faas-cli new api-proxy --lang python3-http

# faas-cli build -f ./api-proxy.yml

cp -r ../apps-example ~/Downloads/osm-faas/
cd  ~/Downloads/osm-faas/

export OPENFAAS_PREFIX=EticaAI
export OPENFAAS_URL=https://osm-faas.etica.ai/
# faas-cli build -f ./osm-api-proxy.yml

# If using https://snapcraft.io/docker, migth need change few things to not use sudo
# and fix the permissions about not run docker outside ~/ (user home)
# e.g error like "unable to evaluate symlinks in Dockerfile path:"
#     cp -r $(pwd)/* ~/Downloads/docker-build-dir
#     cd ~/Downloads/docker-build-dir/function
#     newgrp docker
faas-cli build -f ./api-proxy.yml
faas-cli publish -f ./api-proxy.yml
# faas-cli deploy -f ./osm-api-proxy.yml
faas-cli deploy -f ./api-proxy.yml

docker tag api-proxy:latest ghcr.io/fititnt/api-proxy:latest
docker push ghcr.io/fititnt/api-proxy:latest

```

<!--
> See more repos https://github.com/search?o=desc&q=openfaas+image&s=updated&type=Repositories
... https://github.com/faas-and-furious/openfaas-mememachine
... telegram bot https://github.com/vkonst/openfaas-tgsend
-->
<!--

Create token fititnt-tocken-classic+restricted_packages__up-to_2026-02-28
https://github.com/settings/tokens/new?scopes=write:packages

export CR_PAT=YOUR_TOKEN
echo $CR_PAT | docker login ghcr.io -u fititnt --password-stdin
-->