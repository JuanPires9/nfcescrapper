import sys
import os
from bs4 import BeautifulSoup
import pprint

# adiciona src no path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

# IMPORT CERTO
from scrapers.parsers import NfceParser

with open("nota.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "lxml")

parser = NfceParser()
resultado = parser.parse(soup)

pprint.pprint(resultado)