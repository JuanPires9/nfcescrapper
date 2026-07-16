import sys
import os
import asyncio
import pprint
from bs4 import BeautifulSoup

# Adiciona o diretório src ao python path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from services.qr_service import extract_qr_from_image
from drivers.rest.html_fetcher import fetch_html
from scrapers.parsers import NfceParser
from scrapers.scrapers import NfceScraper


def print_help():
    print("Uso do Script de Diagnóstico:")
    print("  python diagnose.py qr <caminho_da_imagem>")
    print("    -> Testa a extração do link do QR Code de um arquivo de imagem.")
    print("  python diagnose.py fetch <url_do_qr>")
    print("    -> Testa se o cliente HTTP (httpx) consegue baixar o HTML real da URL.")
    print("  python diagnose.py selenium <url_do_qr>")
    print("    -> Testa a captura do HTML via Selenium (Firefox Headless) e faz o parsing.")
    print("  python diagnose.py parse <caminho_do_arquivo_html>")
    print("    -> Testa o parser NFC-e em um arquivo HTML local e exibe o JSON resultante.")


async def run_fetch(url):
    print(f"[*] Executando requisição HTTP GET para: {url}")
    try:
        html = await fetch_html(url)
        print("[+] Sucesso ao baixar a página!")
        print(f"[+] Tamanho do HTML retornado: {len(html)} bytes")

        # Escreve o HTML retornado em um arquivo para inspeção
        output_file = "debug_fetch.html"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"[+] HTML salvo em '{output_file}' para análise.")

        # Verifica assinaturas comuns do portal ou de bloqueios/firewalls
        if "/TSPD/" in html or "APM_DO_NOT_TOUCH" in html:
            print("[WARNING] O portal retornou um desafio de Javascript (F5 BIG-IP WAF).")
            print("          Isso ocorre porque requisições HTTP diretas sem renderização de JS são bloqueadas.")
            print("          Neste caso, a requisição HTTP bruta NÃO retorna os dados da nota fiscal.")
        elif "tabResult" in html:
            print("[+] Identificado a tabela de itens 'tabResult' no HTML!")
            print("[+] O HTML parece ser legítimo e pronto para parseamento.")
        else:
            print("[?] O HTML não contém a tabela 'tabResult' e nem desafios óbvios do F5.")
            print("    Exiba o conteúdo do arquivo 'debug_fetch.html' para inspecionar o que foi retornado.")
    except Exception as e:
        print(f"[-] Erro ao buscar HTML: {type(e).__name__}: {str(e)}")


def run_qr(img_path):
    print(f"[*] Carregando imagem: {img_path}")
    if not os.path.exists(img_path):
        print(f"[-] Arquivo não encontrado: {img_path}")
        return

    with open(img_path, "rb") as f:
        img_bytes = f.read()

    print("[*] Decodificando QR Code (zxing-cpp com fallback OpenCV)...")
    qr_url = extract_qr_from_image(img_bytes)

    if qr_url:
        print(f"[+] QR Code extraído com sucesso!")
        print(f"[+] Link da Nota Fiscal: {qr_url}")
    else:
        print("[-] Nenhum QR Code detectado na imagem. Tente uma foto com melhor resolução, contraste ou menos rotação.")


def run_selenium(url):
    print(f"[*] Iniciando Selenium (Firefox Headless) para carregar a página: {url}")
    print("[*] Aguarde, isso pode levar alguns segundos...")
    try:
        scraper = NfceScraper()
        result = scraper.get(url)
        print("[+] Selenium carregou e parseou a nota fiscal com sucesso!")
        print("[+] Resultado do parsing:")
        pprint.pprint(result)
    except Exception as e:
        print(f"[-] Erro na execução com Selenium: {type(e).__name__}: {str(e)}")


def run_parse(html_path):
    print(f"[*] Carregando arquivo HTML local: {html_path}")
    if not os.path.exists(html_path):
        print(f"[-] Arquivo não encontrado: {html_path}")
        return

    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    print("[*] Parseando HTML com BeautifulSoup (lxml)...")
    soup = BeautifulSoup(html, "lxml")
    parser = NfceParser()
    try:
        result = parser.parse(soup)
        print("[+] Sucesso ao parsear o HTML local!")
        print("[+] Dados Extraídos:")
        pprint.pprint(result)
    except Exception as e:
        print(f"[-] Erro durante o parsing: {type(e).__name__}: {str(e)}")


def main():
    if len(sys.argv) < 3 and not (len(sys.argv) == 2 and sys.argv[1] == "help"):
        print_help()
        sys.exit(1)

    cmd = sys.argv[1]
    arg = sys.argv[2] if len(sys.argv) > 2 else None

    if cmd == "qr":
        run_qr(arg)
    elif cmd == "fetch":
        asyncio.run(run_fetch(arg))
    elif cmd == "selenium":
        run_selenium(arg)
    elif cmd == "parse":
        run_parse(arg)
    else:
        print_help()


if __name__ == "__main__":
    main()
