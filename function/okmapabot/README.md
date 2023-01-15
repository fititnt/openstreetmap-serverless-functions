# function/okmapabot


## Português


```bash

# https://core.telegram.org/bots/api#setwebhook
export TELEGRAM_BOT_TOKEN="..."
# X-Telegram-Bot-Api-Secret-Token
export TELEGRAM_BOT_APISECRET="..."


# Webhook
curl -X POST -H "Content-Type: application/json" --data '{
  "url": "https://osm-faas.etica.ai/function/okmapabot/telegramWebhook",
  "secret_token": "<TELEGRAM_BOT_APISECRET>",
  "allowed_updates": ["message"]
}' https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/setWebhook

# Via webjook
curl -X POST -H "Content-Type: application/json" --data '{
  "commands": [
    {"command":"exemplos","description":"[Habilidade] Lista exemplos de uso"},
    {"command":"dicionario","description":"[Habilidade] Dicionário OpenStreetMap"},
    {"command":"overpassql","description":"[Habilidade] Linguagem de consulta Overpass"},
    {"command":"id","description":"Informações do seu contexto (local, interesses, ...)"},
    {"command":"sobre","description":"Saiba mais"},
    {"command":"debug","description":"Informações de depuração"},
  ]
}' https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/setMyCommands

## Via @BotFather, Inspirado em Alexa Skills https://canaltech.com.br/casa-conectada/amazon-echo-alexa-melhores-comandos-de-voz-151347/
# exemplos - [Habilidade] Lista exemplos de uso
# dicionario - [Habilidade] Dicionário OpenStreetMap
# overpassql - [Habilidade] Linguagem de consulta Overpass
# id - Informações do seu contexto (local, interesses, ...)
# sobre - Saiba mais
# debug - Informações de depuração

```

<!--
## Todos
- https://openstreetmap.community/
-->

<!--

## rebuild drill
cp -r $(pwd)/* ~/Downloads/docker-build
cd ~/Downloads/docker-build

# https://core.telegram.org/bots/api#setwebhook
export TELEGRAM_BOT_TOKEN="..."
# X-Telegram-Bot-Api-Secret-Token
export TELEGRAM_WEBHOOK_SECRET="..."

faas-cli build -f ./stack.yml --filter okmapabot && docker run --name okmapabot --publish 8080:8080 -e TELEGRAM_BOT_TOKEN="$TELEGRAM_BOT_TOKEN" -e TELEGRAM_BOT_APISECRET="$TELEGRAM_BOT_APISECRET" -d ghcr.io/fititnt/okmapabot && docker logs --follow okmapabot

docker container stop okmapabot && docker container rm okmapabot

## Deploy prod
fititnt@bravo:~$ export OPENFAAS_URL=https://osm-faas.etica.ai/
fititnt@bravo:~$ faas-cli deploy --image=ghcr.io/fititnt/okmapabot:latest --secret=secret-okmapabot-telegram-token --secret=secret-okmapabot-telegram-apisecret --env TELEGRAM_BOT_TOKEN_FILE='secret-okmapabot-telegram-token' --env TELEGRAM_BOT_APISECRET_FILE='secret-okmapabot-telegram-apisecret' --name=okmapabot
Function okmapabot already exists, attempting rolling-update.

## Token def on Telegram
# Configure telegram webhook first time. Change <TELEGRAM_BOT_TOKEN> and ?url=
curl https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/setWebhook?url=https://osm-faas.etica.ai/function/wiki-telegram-bot/telegramWebhook/bot<TELEGRAM_BOT_TOKEN>
#   > {"ok":true,"result":true,"description":"Webhook was set"}

## Simulate telegram call

### Texto

curl --tlsv1.2 -v -k -X POST -H "Content-Type: application/json" -H "Cache-Control: no-cache"  -H "X-Telegram-Bot-Api-Secret-Token: $TELEGRAM_WEBHOOK_SECRET" -d '{
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
  "text":"casa"
}
}' "http://localhost:8080/telegramWebhook/"

# }' "https://osm-faas.etica.ai/function/okmapabot/"

### Overpass QL

curl --tlsv1.2 -v -k -X POST -H "Content-Type: application/json" -H "Cache-Control: no-cache"  -H "X-Telegram-Bot-Api-Secret-Token: $TELEGRAM_WEBHOOK_SECRET" -d '{
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
  "text":"/overpassql data=node[name='Gielgen'];out;"
}
}' "http://localhost:8080/telegramWebhook/"


### Simulate raw upload with curl
echo "data=node[name='Gielgen'];out;" > query.osm
curl "https://faas.example.org/overpass-proxy" --data @query.osm --output output.osm

curl -F document=@output.osm https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendDocument?chat_id=131936548

-->

