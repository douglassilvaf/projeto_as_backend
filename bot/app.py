import sys
import asyncio
import os

from flask import Flask, request, Response
from botbuilder.core import (
    BotFrameworkAdapter,
    BotFrameworkAdapterSettings,
    TurnContext,
    ConversationState,
    MemoryStorage,
    UserState,
)
from botbuilder.schema import Activity, ActivityTypes

# Importações dos diálogos (ajustadas para importação direta, pois estamos executando app.py no diretório 'bot')
from dialogs import MainDialog, MatriculaDialog
from config import DefaultConfig

# Importações adicionais necessárias para gerenciar diálogos
from botbuilder.dialogs import DialogSet, DialogTurnStatus
from botbuilder.dialogs.prompts import (
    TextPrompt,
    PromptOptions,
)

# Carrega as configurações do bot
CONFIG = DefaultConfig()

# Cria a aplicação Flask
app = Flask(__name__, instance_relative_config=True)

# Tenta carregar as configurações da aplicação Flask
try:
    app.config.from_object("config.DefaultConfig")
except Exception as e:
    print(f"Erro ao carregar a configuração: {e}", file=sys.stderr)
    sys.exit(1)

# Configura o BotFrameworkAdapter com as credenciais do bot
SETTINGS = BotFrameworkAdapterSettings(CONFIG.APP_ID, CONFIG.APP_PASSWORD)
ADAPTER = BotFrameworkAdapter(SETTINGS)

# Função de tratamento de erros para o adaptador do bot
async def on_error(context: TurnContext, error: Exception):
    # Imprime o erro no console (para depuração local)
    print(f"\n [on_error] Erro não tratado: {error}", file=sys.stderr)

    # Envia uma mensagem amigável para o usuário
    await context.send_activity("Opa! Parece que algo deu errado.")

    # Limpa o estado da conversa para evitar loops de erro (pode falhar se o estado não foi inicializado)
    try:
        await conversation_state.delete(context)
    except KeyError:
        # Se ocorrer KeyError ao tentar limpar o estado, apenas loga e continua
        print(f"\n [on_error] Erro ao tentar limpar o estado da conversa (KeyError).", file=sys.stderr)


# Define o manipulador de erros para o adaptador
ADAPTER.on_turn_error = on_error

# Cria os objetos de armazenamento e estado para a conversa e o usuário
memory_storage = MemoryStorage()
conversation_state = ConversationState(memory_storage)
user_state = UserState(memory_storage)

# Cria a propriedade para o estado do diálogo no ConversationState
dialog_state_property = conversation_state.create_property("DialogState")

# Cria o DialogSet, que é responsável por gerenciar o fluxo dos diálogos
dialogs = DialogSet(dialog_state_property)

# Cria as instâncias dos diálogos
main_dialog = MainDialog(conversation_state) # Passa o conversation_state para o MainDialog
matricula_dialog = MatriculaDialog()

# Adiciona os diálogos ao DialogSet para que possam ser gerenciados
dialogs.add(main_dialog)
dialogs.add(matricula_dialog)

# Rota principal para o recebimento de mensagens do Bot Framework Emulator/Serviço
@app.route("/api/messages", methods=["POST"])
async def messages():
    # Verifica o tipo de conteúdo da requisição
    if "application/json" in request.headers["Content-Type"]:
        body = request.json
    else:
        # Retorna erro 415 se o tipo de conteúdo não for JSON
        return Response(status=415)

    # Deserializa o corpo da requisição em um objeto Activity
    activity = Activity().deserialize(body)

    # Obtém o cabeçalho de autorização, se presente
    auth_header = request.headers["Authorization"] if "Authorization" in request.headers else ""

    try:
        # Define a função que será executada para cada turno de conversa
        async def turn_function(turn_context: TurnContext):
            # Cria um contexto de diálogo para o turno atual
            dialog_context = await dialogs.create_context(turn_context)

            # Lógica para processar diferentes tipos de atividades
            if turn_context.activity.type == ActivityTypes.message:
                # Se for uma mensagem, tenta continuar um diálogo existente
                dialog_result = await dialog_context.continue_dialog()
                # Se nenhum diálogo estava ativo após continue_dialog,
                # e a mensagem não está vazia (para evitar loops em atividades vazias),
                # inicie o MainDialog.
                if dialog_result.status == DialogTurnStatus.Empty and turn_context.activity.text:
                    await dialog_context.begin_dialog(main_dialog.id)

            elif turn_context.activity.type == ActivityTypes.conversation_update:
                # Se for uma atualização de conversa (ex: bot adicionado à conversa)
                # Verifica se o bot foi adicionado como um novo membro
                if turn_context.activity.members_added and turn_context.activity.recipient.id in [member.id for member in turn_context.activity.members_added]:
                    # Inicia o MainDialog. A saudação inicial e o menu
                    # serão feitos dentro do greet_and_prompt_menu_step.
                    await dialog_context.begin_dialog(main_dialog.id)
            else:
                # Para outros tipos de atividade, loga a atividade (opcional)
                await turn_context.send_activity(f"[{turn_context.activity.type}] atividade detectada")

        # Processa a atividade usando o adaptador e a função de turno definida
        await ADAPTER.process_activity(activity, auth_header, turn_function)
        
        # Retorna uma resposta HTTP 200 OK para o chamador (Emulator/Serviço)
        return Response(status=200)

    except Exception as e:
        # Em caso de exceção, o manipulador on_error do adaptador será chamado
        # Nenhuma ação adicional de retorno é necessária aqui, pois o Flask já
        # tratará a exceção via on_error configurado no ADAPTER.
        raise e

# Bloco principal para iniciar o servidor Flask quando o script é executado diretamente
if __name__ == "__main__":
    try:
        # Inicia a aplicação Flask em modo de depuração na porta 3978 (padrão para bots)
        app.run(debug=True, port=3978)
    except Exception as e:
        print(f"Erro ao iniciar a aplicação: {e}", file=sys.stderr)
        sys.exit(1)

