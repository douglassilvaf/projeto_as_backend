import json
import re  # Importa a biblioteca de Expressões Regulares para validar o e-mail
from typing import List

from botbuilder.core import (
    ActivityHandler,
    MessageFactory,
    TurnContext,
    ConversationState,
)
from botbuilder.schema import (
    ChannelAccount,
    CardAction,
    ActionTypes,
    SuggestedActions,
)

# CLASSE AUXILIAR para organizar os dados da matrícula no estado
class DadosMatricula:
    def __init__(self, etapa: str = None, nome: str = None, email: str = None, curso: str = None):
        self.etapa = etapa  # Controla a etapa atual da conversa (pedir_nome, pedir_email, etc.)
        self.nome = nome
        self.email = email
        self.curso = curso

class MeuBot(ActivityHandler):
    def __init__(self, conversation_state: ConversationState):
        if conversation_state is None:
            raise TypeError("[MeuBot]: Parâmetro 'conversation_state' não pode ser None.")
        self.conversation_state = conversation_state
        self.matricula_state_accessor = self.conversation_state.create_property("DadosMatricula")

        try:
            with open("faq.json", "r", encoding="utf-8") as f:
                self.faq_data = json.load(f)
        except FileNotFoundError:
            print("Erro: O arquivo faq.json não foi encontrado.")
            self.faq_data = {}

    async def on_turn(self, turn_context: TurnContext):
        await super().on_turn(turn_context)
        await self.conversation_state.save_changes(turn_context, False)

    async def on_members_added_activity(self, members_added: List[ChannelAccount], turn_context: TurnContext):
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                texto_boas_vindas = "Olá! Sou o bot de atendimento. Selecione uma das opções abaixo."
                reply = MessageFactory.text(texto_boas_vindas)
                reply.suggested_actions = self.criar_botoes_iniciais()
                await turn_context.send_activity(reply)

    def criar_botoes_iniciais(self):
        botoes = [CardAction(type=ActionTypes.im_back, title=pergunta.capitalize(), value=pergunta) for pergunta in self.faq_data.keys()]
        botoes.append(CardAction(type=ActionTypes.im_back, title="Realizar Matrícula", value="realizar matrícula"))
        return SuggestedActions(actions=botoes)

    # ESTA FUNÇÃO CONTÉM TODA A NOVA LÓGICA
    async def on_message_activity(self, turn_context: TurnContext):
        # Primeiro, obtemos o estado atual da matrícula na conversa.
        # Se não existir, um novo objeto DadosMatricula é criado.
        dados_matricula = await self.matricula_state_accessor.get(turn_context, lambda: DadosMatricula())
        texto_recebido = turn_context.activity.text.strip()

        # --- LÓGICA DA MÁQUINA DE ESTADOS ---

        # ETAPA 0: O usuário ainda não iniciou a matrícula e está interagindo com o FAQ ou iniciando o processo
        if dados_matricula.etapa is None:
            if texto_recebido.lower() == "realizar matrícula":
                # Inicia o fluxo, define a primeira etapa e faz a primeira pergunta
                dados_matricula.etapa = "pedir_nome"
                await turn_context.send_activity("Entendido! Vamos iniciar o processo de matrícula.")
                await turn_context.send_activity("Para começar, qual é o seu nome completo?")
            else:
                # Lógica do FAQ (continua a mesma)
                resposta = self.faq_data.get(texto_recebido.lower())
                if resposta:
                    await turn_context.send_activity(resposta)
                else:
                    texto_erro = "Desculpe, não entendi. Gostaria de ver as opções novamente?"
                    reply = MessageFactory.text(texto_erro)
                    reply.suggested_actions = self.criar_botoes_iniciais()
                    await turn_context.send_activity(reply)
            return # Sai da função após tratar a mensagem

        # ETAPA 1: O bot pediu o nome, então a mensagem atual é o nome do usuário
        if dados_matricula.etapa == "pedir_nome":
            dados_matricula.nome = texto_recebido
            dados_matricula.etapa = "pedir_email" # Atualiza para a próxima etapa
            await turn_context.send_activity(f"Obrigado, {dados_matricula.nome}.")
            await turn_context.send_activity("Agora, por favor, informe o seu melhor e-mail.")
            return

        # ETAPA 2: O bot pediu o e-mail
        if dados_matricula.etapa == "pedir_email":
            # Validação simples de e-mail usando expressão regular
            if re.match(r"[^@]+@[^@]+\.[^@]+", texto_recebido):
                dados_matricula.email = texto_recebido
                dados_matricula.etapa = "pedir_curso" # Atualiza para a próxima etapa
                await turn_context.send_activity("E-mail registrado! Para qual curso você gostaria de se matricular?")
            else:
                # Se o e-mail for inválido, pede novamente sem mudar de etapa
                await turn_context.send_activity("Opa, parece que este e-mail não é válido. Por favor, tente novamente.")
            return

        # ETAPA 3: O bot pediu o curso
        if dados_matricula.etapa == "pedir_curso":
            dados_matricula.curso = texto_recebido
            
            # Fim do fluxo! Mostra um resumo e limpa o estado.
            await turn_context.send_activity("Ótimo! Sua pré-matrícula foi registrada com sucesso.")
            
            resumo = (
                f"Aqui está o resumo dos seus dados:\n\n"
                f"**Nome:** {dados_matricula.nome}\n\n"
                f"**E-mail:** {dados_matricula.email}\n\n"
                f"**Curso:** {dados_matricula.curso}"
            )
            await turn_context.send_activity(resumo)
            
            # Limpa o estado para a próxima conversa
            await self.matricula_state_accessor.delete(turn_context)
            
            # Oferece as opções iniciais novamente
            texto_final = "Se precisar de algo mais, é só escolher uma das opções."
            reply = MessageFactory.text(texto_final)
            reply.suggested_actions = self.criar_botoes_iniciais()
            await turn_context.send_activity(reply)
            return