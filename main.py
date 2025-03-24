# 📘 ATA IELB IA – API com Flask + Notion (campos da tabela + corpo das páginas)
# ---------------------------------------------------------------

from flask import Flask, request, jsonify
from notion_client import Client
import os

app = Flask(__name__)

# 🔐 Variáveis seguras no ambiente do Render
notion_token = os.getenv("NOTION_TOKEN")
database_id = os.getenv("DATABASE_ID")
notion = Client(auth=notion_token)

@app.route("/")
def home():
    return "✅ API IELB IA conectada ao Notion (campos e conteúdo)!"

@app.route("/buscar", methods=["POST"])
def buscar():
    data = request.get_json()
    termo = data.get("termo", "").lower()
    resultados = []

    try:
        response = notion.databases.query(database_id=database_id)
        for page in response["results"]:
            page_id = page["id"]
            props = page["properties"]

            titulo = props.get("Título da Ata", {}).get("title", [])
            quem = props.get("Quem", {}).get("select", {}).get("name", "")
            ano = props.get("Ano", {}).get("date", {}).get("start", "")
            reuniao = props.get("Reunião", {}).get("rich_text", [])
            link_txt = props.get("Link do .txt", {}).get("url", "")

            titulo_texto = titulo[0]["text"]["content"] if titulo else ""
            reuniao_texto = reuniao[0]["text"]["content"] if reuniao else ""

            # Verificar se o termo aparece nos campos
            campos = [titulo_texto, quem, ano, reuniao_texto, link_txt]
            match_campo = any(termo in (str(c) or '').lower() for c in campos)

            # Verificar se aparece no corpo do texto
            match_corpo = False
            trecho = ""
            try:
                blocks = notion.blocks.children.list(page_id=page_id)["results"]
                texto_completo = " ".join(
                    block["paragraph"]["rich_text"][0]["text"]["content"]
                    for block in blocks
                    if block["type"] == "paragraph" and block["paragraph"]["rich_text"]
                )
                if termo in texto_completo.lower():
                    match_corpo = True
                    trecho = extrair_trecho(texto_completo, termo)
            except:
                pass

            if match_campo or match_corpo:
                resultados.append({
                    "ata": titulo_texto,
                    "ano": ano,
                    "quem": quem,
                    "reuniao": reuniao_texto,
                    "trecho": trecho or "Trecho nos campos da tabela",
                    "link": link_txt
                })

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

    return jsonify(resultados)

# 🔍 Destacar o trecho do texto

def extrair_trecho(texto, termo, contexto=150):
    pos = texto.lower().find(termo)
    if pos == -1:
        return ""
    inicio = max(0, pos - contexto)
    fim = min(len(texto), pos + len(termo) + contexto)
    return texto[inicio:fim].strip()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
