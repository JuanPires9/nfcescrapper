import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse

from drivers.rest.exceptions_handler import exception_container
from .routers import (
    companies_router,
    invoices_router,
    items_router,
    products_router,
    users_router,
)

app = FastAPI()

app.include_router(products_router)
app.include_router(companies_router)
app.include_router(invoices_router)
app.include_router(items_router)
app.include_router(users_router)


@app.get("/", response_class=RedirectResponse)
async def redirect_to_scanner():
    return RedirectResponse(url="/scanner")


@app.get("/scanner", response_class=HTMLResponse)
async def get_scanner():
    template_path = os.path.join(
        os.path.dirname(__file__), "templates", "scanner.html"
    )
    with open(template_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)


exception_container(app)

