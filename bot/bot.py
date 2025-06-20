import json
import re
from typing import List
import aiohttp  # Importamos a biblioteca para fazer as chamadas HTTP

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

class ConversationFlow:
    def __init__(self, menu_atual: str = "principal", etapa_matricula: str = None, nome: str = None, email: str = None, curso: str = None):
        self.menu_atual = menu_atual
        self.etapa_matricula = etapa_matricula
        self.nome = nome
        self.email = email
        self.curso = curso

class MeuBot(ActivityHandler):
    def __init__(self, conversation_state: ConversationState):
        self.conversation_state = conversation_state
        self.flow_accessor = self.conversation_state.create_property("ConversationFlow")
        try:
            with open("faq.json", "r", encoding="utf-8") as f:
                self.faq_data = json.load(f)
        except FileNotFoundError:
            self.faq_data = {}

    async def on_turn(self, turn_context: TurnContext):
        await super().on_turn(turn_context)
        await self.conversation_state.save_changes(turn_context, False)

    async def on_members_added_activity(self, members_added: List[ChannelAccount], turn_context: TurnContext):
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                await self.mostrar_menu_principal(turn_context, "Olá! Sou o bot de atendimento. Selecione uma das opções abaixo.")

    def criar_botoes_principais(self):
        botoes = [
            CardAction(type=ActionTypes.im_back, title="Perguntas Frequentes", value="perguntas frequentes"),
            CardAction(type=ActionTypes.im_back, title="Realizar Matrícula", value="realizar matrícula")
        ]
        return SuggestedActions(actions=botoes)

    def criar_botoes_faq(self):
        botoes = [CardAction(type=ActionTypes.im_back, title=pergunta.capitalize(), value=pergunta) for pergunta in self.faq_data.keys()]
        botoes.append(CardAction(type=ActionTypes.im_back, title="⬅️ Voltar", value="voltar"))
        return SuggestedActions(actions=botoes)

    async def mostrar_menu_principal(self, turn_context: TurnContext, texto: str):
        reply = MessageFactory.text(texto)
        reply.suggested_actions = self.criar_botoes_principais()
        await turn_context.send_activity(reply)

    async def mostrar_menu_faq(self, turn_context: TurnContext, texto: str):
        reply = MessageFactory.text(texto)
        reply.suggested_actions = self.criar_botoes_faq()
        await turn_context.send_activity(reply)

    # --- NOVA FUNÇÃO PARA ENVIAR DADOS AO BACKEND ---
    async def enviar_dados_para_backend(self, flow: ConversationFlow) -> bool:
        url = "https://api-matricula-douglas-adbkb2befehghqe7.brazilsouth-01.azurewebsites.net/api/matriculas"
        dados_post = {"nome": flow.nome, "email": flow.email, "curso": flow.curso}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=dados_post) as response:
                    if response.status == 200:
                        print(">>> SUCESSO: Dados enviados para o backend com sucesso.")
                        response_json = await response.json()
                        print(f">>> Matrícula salva com ID: {response_json.get('id')}")
                        return True
                    else:
                        print(f">>> ERRO: Falha ao enviar dados para o backend. Status: {response.status}")
                        return False
        except Exception as e:
            print(f">>> EXCEÇÃO: Ocorreu um erro ao tentar conectar com o backend: {e}")
            return False

    async def on_message_activity(self, turn_context: TurnContext):
        flow = await self.flow_accessor.get(turn_context, lambda: ConversationFlow())
        texto_recebido = turn_context.activity.text.lower().strip()

        if texto_recebido == "voltar" and flow.menu_atual == "faq":
            flow.menu_atual = "principal"
            await self.mostrar_menu_principal(turn_context, "Voltando ao menu principal.")
            return

        if flow.menu_atual == "principal":
            if texto_recebido == "perguntas frequentes":
                flow.menu_atual = "faq"
                await self.mostrar_menu_faq(turn_context, "Selecione uma das perguntas abaixo:")
            elif texto_recebido == "realizar matrícula":
                flow.menu_atual = "matricula"
                flow.etapa_matricula = "pedir_nome"
                await turn_context.send_activity("Entendido! Vamos iniciar a matrícula. Para começar, qual é o seu nome completo?")
            else:
                 await self.mostrar_menu_principal(turn_context, "Desculpe, não entendi. Por favor, escolha uma das opções.")
        
        elif flow.menu_atual == "faq":
            resposta = self.faq_data.get(texto_recebido)
            if resposta:
                await turn_context.send_activity(resposta)
                await self.mostrar_menu_faq(turn_context, "Posso ajudar com outra pergunta?")
            else:
                await self.mostrar_menu_faq(turn_context, "Não encontrei essa pergunta. Por favor, selecione uma das opções.")

        elif flow.menu_atual == "matricula":
            if flow.etapa_matricula == "pedir_nome":
                flow.nome = turn_context.activity.text.strip()
                flow.etapa_matricula = "pedir_email"
                await turn_context.send_activity(f"Obrigado, {flow.nome}. Agora, informe seu melhor e-mail.")
            
            elif flow.etapa_matricula == "pedir_email":
                email = turn_context.activity.text.strip()
                if re.match(r"[^@]+@[^@]+\.[^@]+", email):
                    flow.email = email
                    flow.etapa_matricula = "pedir_curso"
                    await turn_context.send_activity("E-mail registrado! Para qual curso deseja se matricular?")
                else:
                    await turn_context.send_activity("Opa, e-mail inválido. Por favor, tente novamente.")

            elif flow.etapa_matricula == "pedir_curso":
                flow.curso = turn_context.activity.text.strip()
                
                # --- CHAMADA PARA A API ACONTECE AQUI! ---
                sucesso_envio = await self.enviar_dados_para_backend(flow)
                
                if sucesso_envio:
                    resumo = (f"Ótimo! Sua pré-matrícula foi registrada com sucesso em nosso sistema.\n\n"
                              f"**Nome:** {flow.nome}\n\n**E-mail:** {flow.email}\n\n**Curso:** {flow.curso}")
                else:
                    resumo = "Concluímos a coleta dos seus dados, mas houve um problema ao registrá-los em nosso sistema. Por favor, tente novamente mais tarde."
                
                await turn_context.send_activity(resumo)
                await self.flow_accessor.set(turn_context, ConversationFlow(menu_atual="principal"))
                await self.mostrar_menu_principal(turn_context, "Se precisar de algo mais, estou à disposição.")