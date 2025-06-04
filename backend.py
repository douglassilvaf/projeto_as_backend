from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/matriculas', methods=['POST'])
def matriculas():
    try:
        data = request.get_json()
        nome = data['nome']
        email = data['email']
        curso = data['curso']

        # Aqui você pode salvar em banco, arquivo, etc.
        print(f"Recebido matrícula: Nome={nome}, Email={email}, Curso={curso}")

        return jsonify({"message": "Matrícula recebida com sucesso!"}), 200

    except Exception as e:
        return jsonify({"error": "Dados inválidos ou incompletos.", "details": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
