import os
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager


__all__ = ["get_browser"]


def get_browser() -> Firefox:
    """Get a headless Firefox browser

    Returns:
        Firefox: headless Firefox browser
    """
    options = Options()
    options.add_argument("--headless")
    # Evita detecção de bot pelos portais de segurança da SEFAZ
    options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0")
    options.set_preference("dom.webdriver.enabled", False)
    # Configura o binário do Firefox se estiver rodando no Linux/Docker
    if os.path.exists("/usr/bin/firefox-esr"):
        options.binary_location = "/usr/bin/firefox-esr"
    elif os.path.exists("/usr/bin/firefox"):
        options.binary_location = "/usr/bin/firefox"

    WEBDRIVER_PATH = os.environ.get("WEBDRIVER_PATH")

    if not WEBDRIVER_PATH or not os.path.exists(WEBDRIVER_PATH):
        WEBDRIVER_PATH = GeckoDriverManager().install()

    service = Service(WEBDRIVER_PATH)
    browser = Firefox(service=service, options=options)

    return browser
