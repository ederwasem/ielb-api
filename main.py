from flask import Flask, request, jsonify
import openai

app = Flask(__name__)

# Chave secreta da OpenAI
openai.api_key = "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"

@app.route("/")
def home():
    return "✅ API IELB rodando no Render!"

@app.route("/buscar", methods=["POST"])
def buscar():
    data = request.get_json()
    termo = data.get("termo", "").lower()

    atas_mock = {
        "DN 1997-01": "Chamado do pastor Jonas em 1997 aprovado.",
        "DN 2001-04": "Reconhecimento do trabalho do pastor Jonas na missão urbana.",
        "DN 2022-02": "Nada consta sobre o referido pastor."
    }

    resultados = []
    for nome_ata, texto in atas_mock.items():
        if termo in texto.lower():
            resultados.append({
                "ata": nome_ata,
                "trecho": texto
            })

    return jsonify(resultados)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
