# 🚀 Projeto AS Backend

Este é o backend do projeto acadêmico desenvolvido para a disciplina de Análise de Sistemas, com foco na criação de uma API robusta e funcional para comunicação com um chatbot. O projeto está sendo desenvolvido utilizando o **Bot Framework SDK** e uma estrutura RESTful para responder às interações do usuário.

## 📌 Objetivo

O principal objetivo é permitir a comunicação entre um bot e usuários via terminal, respondendo perguntas e interagindo com base em regras definidas no backend. Com isso, testamos habilidades como:

- Desenvolvimento de APIs REST
- Integração com chatbot via JSON
- Estruturação de rotas e lógica de negócios

---

## ⚙️ Tecnologias Utilizadas

- **Python 3.x**
- **FastAPI** – Framework web para criação de APIs rápidas e modernas
- **Uvicorn** – Servidor ASGI leve e eficiente
- **Pydantic** – Validação de dados com base em tipagem
- **Bot Framework SDK** – Para gerenciar mensagens e fluxos do bot
- **JSON** – Como formato principal de entrada/saída

---

## 📁 Estrutura do Projeto

```

projeto\_as\_backend/
│
├── app/
│   ├── main.py            # Arquivo principal da aplicação FastAPI
│   ├── models/            # Modelos de dados (Pydantic)
│   ├── routes/            # Rotas da API
│   └── services/          # Regras de negócio
│
├── tests/                 # Testes unitários
├── requirements.txt       # Dependências do projeto
└── README.md              # Este arquivo

````

---

## ▶️ Como Executar Localmente

1. **Clone o repositório**
   ```bash
   git clone https://github.com/douglassilvaf/projeto_as_backend.git
   cd projeto_as_backend
````

2. **Crie e ative um ambiente virtual**

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   .\venv\Scripts\activate   # Windows
   ```

3. **Instale as dependências**

   ```bash
   pip install -r requirements.txt
   ```

4. **Execute o servidor**

   ```bash
   uvicorn app.main:app --reload
   ```

5. **Acesse a API**

   * Documentação Swagger: [http://localhost:8000/docs](http://localhost:8000/docs)
   * Redoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 📬 Exemplos de Requisição (JSON)

```json
POST /mensagem
Content-Type: application/json

{
  "usuario": "João",
  "mensagem": "Quero começar o teste"
}
```

```json
Resposta:
{
  "resposta": "Olá João! Vamos começar com perguntas de nível iniciante."
}
```

---

## 🧪 Testes

Execute os testes com:

```bash
pytest
```

---

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir uma **Issue** ou enviar um **Pull Request** com melhorias, correções ou sugestões.

---

## 📄 Licença

Este projeto é licenciado sob a [MIT License](LICENSE).

---

## 👨‍💻 Desenvolvido por

Douglas Silva – [@douglassilvaf](https://github.com/douglassilvaf)
Projeto universitário - IBMEC / Curso de Tecnologia da Informação

---

```

Se quiser personalizar ainda mais, posso adicionar badges, instruções de deploy, ou exemplos específicos das rotas se você me mostrar o conteúdo do `main.py` ou estrutura do bot. Deseja que eu também gere um `requirements.txt` com base nas libs mencionadas?
```
