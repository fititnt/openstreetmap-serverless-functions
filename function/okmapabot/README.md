# function/okmapabot


## Português




```bash

# https://core.telegram.org/bots/api#setwebhook
export TELEGRAM_BOT_TOKEN="..."
# X-Telegram-Bot-Api-Secret-Token
export TELEGRAM_BOT_APISECRET_FILE="..."



# Webhook
curl -X POST -H "Content-Type: application/json" --data '{
  "url": "https://osm-faas.etica.ai/function/okmapabot/telegramWebhook",
  "secret_token": "<TELEGRAM_BOT_APISECRET_FILE>",
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
fititnt@bravo:~$ faas-cli deploy --image=ghcr.io/fititnt/okmapabot:latest --secret=secret-okmapabot-telegram-token --secret=secret-okmapabot-telegram-apisecret --env TELEGRAM_BOT_TOKEN_FILE='secret-okmapabot-telegram-token' --env TELEGRAM_BOT_APISECRET_FILE='secret-okmapabot-telegram-apisecret' --name=okmapabot
Function okmapabot already exists, attempting rolling-update.
-->

<!--
## Todos
- https://openstreetmap.community/
-->