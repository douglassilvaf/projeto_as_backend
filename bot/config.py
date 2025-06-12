class DefaultConfig:
    APP_ID = "" # Vazio para uso local ou preenchido para Azure Bot Service
    APP_PASSWORD = "" # Vazio para uso local ou preenchido para Azure Bot Service

    # Perguntas Frequentes
    FAQ_DATA = {
        "qual o calendário acadêmico?": "O calendário está disponível em: www.exemplo.edu/calendario",
        "como emitir boleto?": "Acesse o portal do aluno e clique em 'Financeiro'.",
        "quais os horários de aula?": "De segunda a sexta, das 19h às 22h.",
        "secretaria": "Você pode contatar a secretaria em secretaria@exemplo.edu ou pelo telefone (XX) XXXX-XXXX.",
        "matricula": "Para iniciar o processo de matrícula, digite 'matricula' ou 'quero me matricular'."
    }

    # URL do Backend (ajuste se seu backend estiver em outro lugar)
    BACKEND_URL = "http://localhost:8080/api/matriculas"