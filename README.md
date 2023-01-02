# openstreetmap-serverless-functions
**[working-draft] Collection of serverless functions ([OpenFaas spec](https://www.openfaas.com/)) for use with OpenStreetMap™.**

[![OpenFaas](img/openfaas-whale.png)](https://www.openfaas.com/)

> Tip: for sysadmins or people interested in offering hosting, [check the openstreetmap-faas-infra](https://github.com/fititnt/openstreetmap-faas-infra).

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

docker tag api-rdf:latest ghcr.io/fititnt/api-rdf:latest
docker push ghcr.io/fititnt/api-rdf:latest

faas-cli build -f ./api-rdf-local.yml && docker run --name api-rdf --publish 8080:8080 -d ghcr.io/fititnt/api-rdf && docker logs --follow api-rdf
docker container stop api-rdf && docker container rm api-rdf

-->

### curl

> OpenFaaS test function. Not related to OpenStreetMap. Ignore for now.

### overpass-proxy (draft)
- **Environment Variables**
  - `OVERPASS_API_DE_FACTO`: `https://overpass-api.de/api/interpreter`

> See also [Overpass Query Language](https://wiki.openstreetmap.org/wiki/Overpass_API/Overpass_QL)

```bash

echo "data=node[name='Gielgen'];out;" > query.osm
curl "https://faas.example.org/overpass-proxy" --data @query.osm --output output.osm

```

<!--
## rebuild drill
cp -r $(pwd)/* ~/Downloads/docker-build
cd ~/Downloads/docker-build

faas-cli build -f ./stack.yml --filter overpass-proxy && docker run --name overpass-proxy --publish 8080:8080 -d ghcr.io/fititnt/overpass-proxy && docker logs --follow overpass-proxy
docker container stop overpass-proxy && docker container rm overpass-proxy && docker rmi ghcr.io/fititnt/overpass-proxy:latest


-->

### sentimentanalysis

> OpenFaaS test function. Not related to OpenStreetMap. Ignore for now.

### wiki-as-base (draft)
- **Environment Variables**
  - `CACHE_DRIVER`: `sqlite`
  - `CACHE_TTL`: `3600`
  - `WIKI_API`: `https://wiki.openstreetmap.org/w/api.php`
  - `USER_AGENT`: `wiki-as-base/1.0`

<!--
## rebuild drill
cp -r $(pwd)/* ~/Downloads/docker-build
cd ~/Downloads/docker-build

# docker build -t ghcr.io/fititnt/wiki-as-base ./wiki-as-base
# faas-cli build -f ./wiki-as-base-local.yml

faas-cli build -f ./stack.yml --filter wiki-as-base && docker run --name wiki-as-base --publish 8080:8080 -d ghcr.io/fititnt/wiki-as-base && docker logs --follow wiki-as-base
docker container stop wiki-as-base && docker container rm wiki-as-base && docker rmi ghcr.io/fititnt/wiki-as-base:latest

# tests
curl http://localhost:8080/Key:maxspeed
curl http://localhost:8080/User:EmericusPetro/sandbox/Wiki-as-base

@bot /faas__wikiasbase /User:EmericusPetro/sandbox/Wiki-as-base

-->

### wiki-telegram-bot (draft)

> Deprecated. Replaced by wiki-telegram-faasbot.

### wiki-telegram-chatbot (draft)

<!--
## rebuild drill
cp -r $(pwd)/* ~/Downloads/docker-build
cd ~/Downloads/docker-build

faas-cli build -f ./stack.yml --filter wiki-telegram-chatbot && docker run --name wiki-telegram-chatbot --publish 8080:8080 --env TELEGRAM_BOT_TOKEN="$TELEGRAM_BOT_TOKEN" -d ghcr.io/fititnt/wiki-telegram-chatbot && docker logs --follow wiki-telegram-chatbot
docker container stop wiki-telegram-chatbot && docker container rm wiki-telegram-chatbot

# test message
curl --tlsv1.2 -v -k -X POST -H "Content-Type: application/json" -H "Cache-Control: no-cache"  -d '{
"update_id":10000,
"message":{
  "date":1441645532,
  "chat":{
     "last_name":"Test Lastname",
     "id":131936548,
     "first_name":"Test",
     "username":"Test"
  },
  "message_id":1365,
  "from":{
     "last_name":"fititnt",
     "id":131936548,
     "first_name":"Test",
     "username":"Test"
  },
  "text":"ola bot"
}
}' "http://localhost:8080/"


```bash

# Configure telegram webhook first time. Change <TELEGRAM_BOT_TOKEN> and ?url=
curl https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/setWebhook?url=https://osm-faas.etica.ai/function/wiki-telegram-bot
#   > {"ok":true,"result":true,"description":"Webhook was set"}
```
-->
### wiki-telegram-faasbot

- **Environment Variables**
  - `CACHE_DRIVER`: `sqlite`
  - `CACHE_TTL`: `3600`
  - `FAAS_BACKEND`: `https://osm-faas.etica.ai/function/`
  - `FAAS_ALLOWED`: `api-rdf,api-proxy,overpass-proxy,wiki-as-base,nodeinfo,cows`
  - Telegram Token (only one option necessary)
    - `TELEGRAM_BOT_FILE_TOKEN`: `<secret-name>` <sup>[See on OpenFaaS secrets](https://docs.openfaas.com/cli/secrets/)</sup>
    - `TELEGRAM_BOT_TOKEN`: `<your-token-here>`
  - `WIKI_API`: `https://wiki.openstreetmap.org/w/api.php`
  - `WIKI_WIKIASBASE_MAIN_PAGE`: `User:EmericusPetro/sandbox/Wiki-as-base`
- **Requeriments**
  - Created bot on Telegram. See [From BotFather to 'Hello World'](https://core.telegram.org/bots/tutorial)
    - Save the `TELEGRAM_BOT_TOKEN`. This is equivalent to a password. If compromised, re-generate again with BotFather
  - After installing the wiki-telegram-bot, get the public FaaS endpoint and your function path, and tell Telegram API about it. Example:
    - `curl https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/setWebhook?url=https://example.org/function/wiki-telegram-bot`


**Customize /slash commands**

```bash
curl -X POST -H "Content-Type: application/json" --data '{
  "commands": [
    {"command":"faas","description":"Function as a Service proxy"}
  ]
}' https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/setMyCommands
# {"ok":true,"result":true}
```

<!--
```bash

# Configure telegram webhook first time. Change <TELEGRAM_BOT_TOKEN> and ?url=
curl https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/setWebhook?url=https://osm-faas.etica.ai/function/wiki-telegram-bot
#   > {"ok":true,"result":true,"description":"Webhook was set"}
```

<!--
- https://t.me/wikilinksbot
>

<!--
## rebuild drill
cp -r $(pwd)/* ~/Downloads/docker-build
cd ~/Downloads/docker-build

faas-cli build -f ./stack.yml --filter wiki-telegram-bot && docker run --name wiki-telegram-bot --publish 8080:8080 --env TELEGRAM_BOT_TOKEN="$TELEGRAM_BOT_TOKEN" -d ghcr.io/fititnt/wiki-telegram-bot && docker logs --follow wiki-telegram-bot
docker container stop wiki-telegram-bot && docker container rm wiki-telegram-bot

## command line
echo "data=node[name='Gielgen'];out;" > query.osm
curl "http://localhost:8080/" --data @query.osm --output output.osm
curl "http://localhost:8080/overpass-proxy" --data @query.osm --output output.osm

## chatbot
/overpass-proxy data=node[name='Gielgen'];out;

-->
<!--
### Debugging wiki-telegram-bot
- https://core.telegram.org/bots/webhooks
-->

## Guides

### Developers of functions

> TODO: draft this.

Check out <https://docs.openfaas.com/>.

Examples of template-stores available:

- _This repository_
- https://github.com/openfaas/store-functions
- https://github.com/openfaas/python-flask-template
- Any custom Dockerfile <sup>But OpenFaaS require some conventions</sup>

### Sysadmins

Full example of [Infrastructure as Code](https://en.wikipedia.org/wiki/Infrastructure_as_code) with [Ansible](https://en.wikipedia.org/wiki/Ansible_(software)) <s>will be released soon...</s> _but_ OpenFaaS core functionality runs mostly with this <https://github.com/openfaas/faasd/blob/master/cloud-config.txt>.

New! IaC released at https://github.com/fititnt/openstreetmap-faas-infra!

## Disclaimers
<!--
TODO see https://wiki.osmfoundation.org/wiki/Trademark_Policy
-->

OpenStreetMap™ is a trademark of the OpenStreetMap Foundation, and is used with their permission.
This project is not endorsed by or affiliated with the OpenStreetMap Foundation. (via [OSMF Trademark_Policy](https://wiki.osmfoundation.org/wiki/Trademark_Policy))

## License


[![Public Domain](https://i.creativecommons.org/p/zero/1.0/88x31.png)](LICENSE)

Public domain