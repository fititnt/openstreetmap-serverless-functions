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
    {"command":"dicionario","description":"[Tópico] Dicionário OpenStreetMap"},
    {"command":"overpassql","description":"[Tópico] Linguagem de consulta Overpass"},
    {"command":"id","description":"Informações do seu contexto (local, interesses, ...)"},
    {"command":"sobre","description":"Saiba mais"},
    {"command":"debug","description":"Informações de depuração"},
  ]
}' https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/setMyCommands

## Via @BotFather
# dicionario - [Tópico] Dicionário OpenStreetMap
# overpassql - [Tópico] Linguagem de consulta Overpass
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



-->

