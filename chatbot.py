import requests

def main():
    print("=== Chatbot de Matrícula ===")

    # Perguntas para o usuário
    nome = input("Qual seu nome? ")
    email = input("Qual seu email? ")
    curso = input("Qual curso deseja se matricular? ")

    dados = {
        "nome": nome,
        "email": email,
        "curso": curso
    }

    try:
        response = requests.post("http://localhost:5000/api/matriculas", json=dados)
        if response.status_code == 200:
            print("Sucesso:", response.json().get("message"))
        else:
            print("Erro do servidor:", response.json())
    except requests.exceptions.RequestException as e:
        print("Erro na comunicação com o servidor:", e)

if __name__ == "__main__":
    main()
