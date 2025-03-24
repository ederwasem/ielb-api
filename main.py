from flask import Flask, request, jsonify
from notion_client import Client
import os

app = Flask(__name__)

# 🔐 Variáveis de ambiente seguras (inseridas no painel do Render)
notion_token = os.getenv("NOTION_TOKEN")
database_id = os.getenv("DATABASE_ID")
notion = Client(auth=notion_token)

@app.route("/")
def home():
    return "✅ API IELB IA conectada ao Notion e pronta para responder!"

@app.route("/buscar", methods=["POST"])
def buscar():
    data = request.get_json()
    termo = data.get("termo", "").lower()
    resultados = []

    try:
        response = notion.databases.query(database_id=database_id)
        for result in response["results"]:
            props = result["properties"]
            titulo = props.get("Título da Ata", {}).get("title", [])
            texto = props.get("Texto Extraído", {}).get("rich_text", [])
            if titulo and texto:
                titulo_texto = titulo[0]["text"]["content"]
                corpo = texto[0]["text"]["content"]
                if termo in corpo.lower():
                    trecho = extrair_trecho(corpo, termo)
                    resultados.append({
                        "ata": titulo_texto,
                        "trecho": trecho
                    })
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

    return jsonify(resultados)

# 🔎 Função auxiliar para destacar o trecho encontrado
def extrair_trecho(texto, termo, contexto=150):
    pos = texto.lower().find(termo)
    if pos == -1:
        return ""
    inicio = max(0, pos - contexto)
    fim = min(len(texto), pos + len(termo) + contexto)
    return texto[inicio:fim].strip()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
