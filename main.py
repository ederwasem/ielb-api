from flask import Flask, request, jsonify
from notion_client import Client
import os
import time

app = Flask(__name__)

# 🔐 Variáveis seguras no Render
notion_token = os.getenv("NOTION_TOKEN")
database_id = os.getenv("DATABASE_ID")
notion = Client(auth=notion_token)

@app.route("/")
def home():
    return "✅ API IELB IA conectada ao Notion com segurança e blocos tratados!"

@app.route("/buscar", methods=["POST"])
def buscar():
    data = request.get_json()
    termo = data.get("termo", "").lower()
    resultados = []
    start_time = time.time()

    try:
        next_cursor = None
        while True:
            query = notion.databases.query(
                database_id=database_id,
                start_cursor=next_cursor if next_cursor else None
            )

            for page in query["results"]:
                page_id = page["id"]
                props = page["properties"]

                titulo = props.get("Título da Ata", {}).get("title", [])
                quem = props.get("Quem", {}).get("select", {}).get("name", "")
                ano = props.get("Ano", {}).get("date", {}).get("start", "")
                reuniao = props.get("Reunião", {}).get("rich_text", [])
                link_txt = props.get("Link do .txt", {}).get("url", "")

                titulo_texto = titulo[0]["text"]["content"] if titulo else ""
                reuniao_texto = reuniao[0]["text"]["content"] if reuniao else ""

                campos = [titulo_texto, quem, ano, reuniao_texto, link_txt]
                match_campo = any(termo in (str(c) or '').lower() for c in campos)

                match_corpo = False
                trecho = ""

                try:
                    blocks = notion.blocks.children.list(block_id=page_id)["results"]
                    texto_completo = ""
                    for block in blocks:
                        tipo = block.get("type")
                        if tipo and block.get(tipo, {}).get("rich_text"):
                            for rt in block[tipo]["rich_text"]:
                                texto_completo += rt["text"].get("content", "") + " "
                    if termo in texto_completo.lower():
                        match_corpo = True
                        trecho = extrair_trecho(texto_completo, termo)
                except Exception as e:
                    print(f"[BLOCOS] Erro na página {page_id} — {e}")

                if match_campo or match_corpo:
                    resultados.append({
                        "ata": titulo_texto,
                        "ano": ano,
                        "quem": quem,
                        "reuniao": reuniao_texto,
                        "trecho": trecho or "Trecho nos campos da tabela",
                        "link": link_txt
                    })

            if not query.get("has_more"):
                break
            next_cursor = query.get("next_cursor")

            if time.time() - start_time > 25:
                break  # Proteção contra timeout no Render

    except Exception as e:
        print("Erro interno:", e)
        return jsonify({"erro": str(e)}), 500

    return jsonify(resultados)

# 🔎 Destacar trecho encontrado
def extrair_trecho(texto, termo, contexto=150):
    pos = texto.lower().find(termo)
    if pos == -1:
        return ""
    inicio = max(0, pos - contexto)
    fim = min(len(texto), pos + len(termo) + contexto)
    return texto[inicio:fim].strip()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
