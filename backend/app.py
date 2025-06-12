from flask import Flask, request, jsonify

app = Flask(__name__)

# Simulação de um "banco de dados" em memória
matriculas = []

@app.route('/api/matriculas', methods=['POST'])
def registrar_matricula():
    data = request.get_json()
    if not data:
        return jsonify({"erro": "Requisição inválida. JSON esperado."}), 400

    nome = data.get('nome')
    email = data.get('email')
    curso = data.get('curso')

    if not nome or not email or not curso:
        return jsonify({"erro": "Campos 'nome', 'email' e 'curso' são obrigatórios."}), 400

    # Simula o registro no "banco de dados"
    matricula_id = len(matriculas) + 1
    nova_matricula = {
        "id": matricula_id,
        "nome": nome,
        "email": email,
        "curso": curso,
        "status": "registrado"
    }
    matriculas.append(nova_matricula)

    print(f"Nova matrícula registrada: {nova_matricula}") # Para debug local

    return jsonify({
        "mensagem": "Matrícula registrada com sucesso!",
        "matricula_id": matricula_id,
        "dados": nova_matricula
    }), 201

@app.route('/')
def home():
    return "Backend de Matrículas em execução!"

if __name__ == '__main__':
    app.run(debug=True, port=8080)