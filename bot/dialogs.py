from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
)
from botbuilder.dialogs.prompts import (
    TextPrompt,
    PromptOptions,
    ChoicePrompt, # Importado para o menu
    ConfirmPrompt, # Útil para futuras confirmações
)
from botbuilder.core import MessageFactory, TurnContext
from botbuilder.schema import InputHints

from botbuilder.dialogs.choices import Choice # Importado para as opções do ChoicePrompt

import aiohttp
import json

from config import DefaultConfig

class MainDialog(ComponentDialog):
    """
    Diálogo principal do chatbot que gerencia o fluxo de conversas.
    Inclui um menu para navegação entre as funcionalidades.
    """
    def __init__(self, conversation_state: dict):
        super().__init__("MainDialog") # ID do diálogo principal

        # Adiciona os prompts que serão usados neste diálogo ou em seus sub-diálogos
        self.add_dialog(TextPrompt("TextPrompt"))
        self.add_dialog(ChoicePrompt("ChoicePrompt")) # Prompt para escolha de opções

        # Define a sequência de passos do fluxo do diálogo principal (WaterfallDialog)
        self.add_dialog(
            WaterfallDialog(
                "MainWaterfall", # ID do WaterfallDialog
                [
                    self.greet_and_prompt_menu_step, # Passo para saudação e exibição do menu
                    self.process_menu_choice_step,   # Passo para processar a escolha do usuário
                    self.loop_step,                  # Passo para retornar ao menu principal
                ],
            )
        )

        self.initial_dialog_id = "MainWaterfall" # Define o passo inicial do diálogo
        self.conversation_state = conversation_state # Armazena o estado da conversa

    async def greet_and_prompt_menu_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """
        Primeiro passo do MainDialog: Envia uma saudação (se for o início) e exibe o menu principal.
        """
        # Envia a saudação apenas se o diálogo principal for iniciado sem uma mensagem de texto (primeiro contato)
        # ou se veio de um replace_dialog e não houve input específico.
        if step_context.context.activity.text is None or step_context.context.activity.text == "":
            await step_context.context.send_activity("Olá! Eu sou o seu assistente virtual. Como posso ajudar?")

        # Define a mensagem do prompt e as opções de escolha para o menu
        prompt_message = MessageFactory.text("Escolha uma opção:")
        choices = [
            Choice("Perguntas Frequentes"),
            Choice("Realizar Matrícula"),
        ]

        # Apresenta o ChoicePrompt ao usuário
        return await step_context.prompt(
            "ChoicePrompt", # O ID do ChoicePrompt definido acima
            PromptOptions(
                prompt=prompt_message,
                choices=choices,
                retry_prompt=MessageFactory.text("Por favor, escolha uma opção válida da lista."),
            ),
        )

    async def process_menu_choice_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """
        Segundo passo do MainDialog: Processa a escolha feita pelo usuário no menu.
        """
        # A partir de um ChoicePrompt, step_context.result deve ser um FoundChoice object.
        # Caso contrário, houve um problema na validação do prompt ou na entrada do usuário.
        
        user_choice_value = ""
        if step_context.result and hasattr(step_context.result, 'value') and step_context.result.value is not None:
            user_choice_value = step_context.result.value.lower() # Pega o valor da escolha e converte para minúsculas
        else:
            # Se o ChoicePrompt não retornou um valor reconhecível,
            # tenta usar o texto bruto da atividade como fallback (para flexibilidade)
            user_choice_value = step_context.context.activity.text.lower() if step_context.context.activity.text else ""
            await step_context.context.send_activity("Não foi possível processar sua escolha da forma esperada. Tentando uma correspondência textual.")


        # Compara a escolha do usuário (agora em minúsculas)
        if "perguntas frequentes" in user_choice_value: # Usa 'in' para correspondência mais flexível
            # Se o usuário escolheu FAQ, informa como perguntar e passa para o próximo passo para coletar a pergunta
            await step_context.context.send_activity("Por favor, digite sua pergunta sobre calendário, boleto, horários ou secretaria.")
            return await step_context.prompt("TextPrompt", PromptOptions(prompt=MessageFactory.text("Qual sua pergunta?")))
        elif "realizar matrícula" in user_choice_value: # Usa 'in' para correspondência mais flexível
            # Se o usuário escolheu matrícula, inicia o diálogo de Matrícula
            return await step_context.begin_dialog("MatriculaDialog")
        else:
            # Se a escolha não for reconhecida, envia uma mensagem e força o retorno ao menu principal.
            # O ChoicePrompt já teria feito o retry_prompt se a validação interna falhasse.
            # Chegar aqui significa que a entrada não foi correspondida e precisamos resetar o fluxo.
            await step_context.context.send_activity("Desculpe, não entendi sua escolha. Por favor, selecione uma opção válida do menu.")
            return await step_context.replace_dialog(self.initial_dialog_id) # Volta ao menu principal (greet_and_prompt_menu_step)

    async def loop_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """
        Terceiro passo do MainDialog: Processa a resposta da FAQ (se aplicável) e retorna ao menu.
        """
        # Verifica se o passo anterior retornou um resultado (ex: a pergunta da FAQ)
        if step_context.result is not None:
            user_question = str(step_context.result).lower() # Converte o resultado para string e minúsculas

            if user_question in DefaultConfig.FAQ_DATA:
                reply = DefaultConfig.FAQ_DATA[user_question]
                await step_context.context.send_activity(reply)
            else:
                await step_context.context.send_activity("Desculpe, não encontrei uma resposta para sua pergunta frequente. Posso ajudar com 'calendário', 'boleto', 'horários' ou 'secretaria'.")

        # Mensagem para retornar ao menu e reiniciar o diálogo principal (para mostrar o menu novamente)
        await step_context.context.send_activity("Posso ajudar em algo mais?")
        return await step_context.replace_dialog(self.initial_dialog_id)


class MatriculaDialog(ComponentDialog):
    """
    Diálogo para guiar o usuário através do processo de matrícula, coletando dados
    e enviando-os para o backend.
    """
    def __init__(self):
        super().__init__("MatriculaDialog") # ID do diálogo de matrícula

        # Adiciona os prompts específicos para a matrícula
        self.add_dialog(TextPrompt("NomePrompt"))
        self.add_dialog(TextPrompt("EmailPrompt"))
        self.add_dialog(TextPrompt("CursoPrompt"))
        self.add_dialog(TextPrompt("ConfirmacaoPrompt")) # Usado para a confirmação final

        # Define a sequência de passos para o processo de matrícula
        self.add_dialog(
            WaterfallDialog(
                "MatriculaWaterfall", # ID do WaterfallDialog
                [
                    self.nome_step,
                    self.email_step,
                    self.curso_step,
                    self.confirmacao_step,
                    self.enviar_dados_step,
                ],
            )
        )

        self.initial_dialog_id = "MatriculaWaterfall" # Define o passo inicial

    async def nome_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """
        Primeiro passo da matrícula: Solicita o nome completo.
        """
        return await step_context.prompt(
            "NomePrompt",
            PromptOptions(
                prompt=MessageFactory.text("Qual é o seu nome completo?")
            ),
        )

    async def email_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """
        Segundo passo da matrícula: Solicita o e-mail de contato.
        Armazena o nome coletado no passo anterior.
        """
        step_context.values["nome"] = step_context.result # Armazena o nome
        return await step_context.prompt(
            "EmailPrompt",
            PromptOptions(
                prompt=MessageFactory.text("Qual é o seu melhor e-mail para contato?")
            ),
        )

    async def curso_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """
        Terceiro passo da matrícula: Solicita o curso.
        Armazena o e-mail coletado no passo anterior.
        """
        step_context.values["email"] = step_context.result # Armazena o e-mail
        return await step_context.prompt(
            "CursoPrompt",
            PromptOptions(
                prompt=MessageFactory.text("Qual curso você deseja matricular-se?")
            ),
        )

    async def confirmacao_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """
        Quarto passo da matrícula: Exibe os dados coletados para confirmação.
        Armazena o curso coletado no passo anterior.
        """
        step_context.values["curso"] = step_context.result # Armazena o curso
        nome = step_context.values["nome"]
        email = step_context.values["email"]
        curso = step_context.values["curso"]

        # Monta a mensagem de confirmação
        confirm_message = (
            f"Por favor, confirme seus dados:\n"
            f"Nome: {nome}\n"
            f"E-mail: {email}\n"
            f"Curso: {curso}\n\n"
            "Está correto? (sim/não)"
        )
        return await step_context.prompt(
            "TextPrompt", # Usa um TextPrompt simples para 'sim' ou 'não'
            PromptOptions(
                prompt=MessageFactory.text(confirm_message)
            ),
        )

    async def enviar_dados_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """
        Último passo da matrícula: Envia os dados para o backend ou cancela.
        """
        if step_context.result.lower() == "sim":
            # Coleta os dados armazenados
            nome = step_context.values["nome"]
            email = step_context.values["email"]
            curso = step_context.values["curso"]

            payload = {
                "nome": nome,
                "email": email,
                "curso": curso,
            }

            try:
                # Realiza a requisição POST para o backend
                async with aiohttp.ClientSession() as session:
                    async with session.post(DefaultConfig.BACKEND_URL, json=payload) as response:
                        if response.status == 201:
                            await step_context.context.send_activity("Dados enviados para matrícula com sucesso! Entraremos em contato em breve.")
                        else:
                            # Se houver erro no backend, exibe a mensagem de erro
                            error_data = await response.json()
                            await step_context.context.send_activity(f"Ocorreu um erro ao enviar os dados para matrícula: {error_data.get('erro', 'Erro desconhecido')}. Por favor, tente novamente mais tarde.")
                            print(f"Erro no backend: {response.status} - {error_data}")
            except aiohttp.ClientConnectorError as e:
                # Erro de conexão com o backend
                await step_context.context.send_activity(f"Não foi possível conectar-se ao serviço de matrícula. Por favor, verifique se o backend está em execução. Erro: {e}")
            except Exception as e:
                # Outros erros inesperados
                await step_context.context.send_activity(f"Ocorreu um erro inesperado ao processar sua matrícula. Por favor, tente novamente. Erro: {e}")
        else:
            # Se o usuário não confirmou, cancela a matrícula
            await step_context.context.send_activity("Ok, matrícula cancelada. Se desejar, podemos começar novamente.")

        # Finaliza o diálogo de matrícula
        return await step_context.end_dialog()

