from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from scrapers.parsers import NfceParser
from services.qr_service import extract_qr_from_image
from scrapers.scrapers import NfceScraper
import os

app = FastAPI(title="NFC-e API - Mobile Ready")

parser = NfceParser()


class UrlRequest(BaseModel):
    url: str


@app.get("/", response_class=HTMLResponse)
async def get_index():
    template_path = os.path.join(os.path.dirname(__file__), "templates", "index.html")
    with open(template_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

def format_for_erp(data: dict) -> dict:
    if not data or "error" in data:
        return data

    empresa = data.get("empresa", {})
    endereco = data.get("endereco", {})
    informacoes = data.get("informacoes", {})
    tributos = data.get("tributos", {})
    totais = data.get("totais", {})
    itens_dict = data.get("itens", {})

    itens_list = []
    if isinstance(itens_dict, list):
        itens_list = itens_dict
    elif isinstance(itens_dict, dict):
        for code, item in itens_dict.items():
            qty = float(item.get("quantidade", 0))
            price = float(item.get("preco_unitario", 0))
            itens_list.append({
                "codigo_fornecedor": item.get("codigo_produto") or code,
                "codigo_produto": item.get("codigo_produto") or code,
                "descricao_xml": item.get("descricao_produto", ""),
                "descricao_produto": item.get("descricao_produto", ""),
                "ean": None,
                "ncm": None,
                "cfop": None,
                "quantidade": qty,
                "unidade_xml": item.get("unidade_medida", ""),
                "unidade_medida": item.get("unidade_medida", ""),
                "valor_unitario": price,
                "preco_unitario": price,
                "valor_total": qty * price
            })

    return {
        "endereco": endereco,
        "empresa": {
            "cnpj": empresa.get("cnpj"),
            "razao_social": empresa.get("razao_social"),
            "nome_fantasia": empresa.get("razao_social"),
        },
        "informacoes": informacoes,
        "tributos": tributos,
        "totais": {
            **totais,
            "valor_total": totais.get("valor_a_pagar", 0.0),
        },
        "itens": itens_list,
    }


@app.post("/nfce/parse-image")
async def parse_from_image(file: UploadFile = File(...)):
    """
    Fluxo mobile:
    imagem → QR → URL → HTML (Selenium) → parser
    """
    file_bytes = await file.read()

    # 1. extrai QR
    url = extract_qr_from_image(file_bytes)

    if not url:
        return {
            "error": "QR code não encontrado na imagem"
        }

    # 2. baixa e parseia usando Selenium (bypassa WAF)
    try:
        scraper = NfceScraper()
        result = scraper.get(url)
        return format_for_erp(result)
    except Exception as e:
        return {
            "error": f"Erro ao obter nota via Selenium: {str(e)}"
        }


@app.post("/nfce/parse-url")
async def parse_from_url(request: UrlRequest):
    """
    Recebe a URL decodificada pelo frontend, baixa via Selenium e
    retorna os dados da NFC-e parseados.
    """
    try:
        scraper = NfceScraper()
        result = scraper.get(request.url)
        return format_for_erp(result)
    except Exception as e:
        return {
            "error": f"Erro ao obter nota via Selenium: {str(e)}"
        }


