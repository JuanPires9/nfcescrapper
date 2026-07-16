from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from src.scrapers.parsers import NfceParser
from src.services.qr_service import extract_qr_from_image
from src.scrapers.scrapers import NfceScraper
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
        return scraper.get(url)
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
        return scraper.get(request.url)
    except Exception as e:
        return {
            "error": f"Erro ao obter nota via Selenium: {str(e)}"
        }

