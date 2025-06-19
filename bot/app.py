import sys
from aiohttp import web

# NOVAS IMPORTAÇÕES PARA ESTADO
from botbuilder.core import (
    BotFrameworkAdapter,
    BotFrameworkAdapterSettings,
    TurnContext,
    MemoryStorage,          # Armazenamento em memória
    ConversationState,      # Estado da conversa
)
from botbuilder.schema import Activity

from bot import MeuBot

# --- CONFIGURAÇÃO DO ESTADO ---
# 1. Criar o armazenamento em memória. Para produção, usaríamos algo mais robusto.
STORAGE = MemoryStorage()

# 2. Criar o estado da conversa, passando o armazenamento.
CONVERSATION_STATE = ConversationState(STORAGE)
# -----------------------------


SETTINGS = BotFrameworkAdapterSettings("", "")
ADAPTER = BotFrameworkAdapter(SETTINGS)

async def on_error(context: TurnContext, error: Exception):
    print(f"\n[on_error] uma exceção foi encontrada: {error}", file=sys.stderr)
    await context.send_activity("Desculpe, parece que algo deu errado.")
    # Limpa o estado da conversa em caso de erro para não ficar "preso"
    await CONVERSATION_STATE.delete(context)

ADAPTER.on_turn_error = on_error

# Passa o estado da conversa para o nosso bot quando ele é criado
BOT = MeuBot(CONVERSATION_STATE)

async def messages(req: web.Request) -> web.Response:
    if "application/json" not in req.headers["Content-Type"]:
        return web.Response(status=415)

    body = await req.json()
    activity = Activity().deserialize(body)
    auth_header = req.headers["Authorization"] if "Authorization" in req.headers else ""

    try:
        # A chamada para process_activity continua a mesma
        response = await ADAPTER.process_activity(activity, auth_header, BOT.on_turn)
        if response:
            return web.json_response(response.body, status=response.status)
        return web.Response(status=201)
    except Exception as exception:
        raise exception

APP = web.Application()
APP.router.add_post("/api/messages", messages)

if __name__ == "__main__":
    try:
        web.run_app(APP, host="localhost", port=3978)
    except Exception as error:
        raise error