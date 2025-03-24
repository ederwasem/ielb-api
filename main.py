# 📘 ATA IELB IA – API com Flask + Notion + GPT-4 (produção Render)
# ---------------------------------------------------------------

from flask import Flask, request, jsonify
from notion_client import Client
import os

app = Flask(__name__)

# 🔐 Configurar token e ID do banco de dados do Notion
notion_token = "ntn_2841150451471D7bsFdjiJbEvIl03e8s7XYiJYWA..."
database_id = "1be69d75-2782-80f0-8713-edf58fef960e"
notion = Client(auth=notion_token)

@app.route("/")
def home():
    return "✅ API IELB conectada ao Notion!"

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

# 🔍 Função auxiliar para destacar o trecho encontrado
def extrair_trecho(texto, termo, contexto=150):
    pos = texto.lower().find(termo)
    if pos == -1:
        return ""
    inicio = max(0, pos - contexto)
    fim = min(len(texto), pos + len(termo) + contexto)
    return texto[inicio:fim].strip()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
