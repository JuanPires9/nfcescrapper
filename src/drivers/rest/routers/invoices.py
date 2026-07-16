from typing import Annotated
from fastapi import APIRouter, Depends, status, HTTPException


from drivers.rest.dependencies import (
    get_invoices_services,
    validate_id_input,
    get_invoices_repository,
    get_companies_repository,
    get_products_repository,
    get_items_repository,
)
from drivers.rest.schemas.invoices import (
    InvoiceModel,
    InvoicePatchRequestModel,
    InvoicePostRequestModel,
    ScrapeInvoiceRequestModel,
)
from services import InvoiceService
from scrapers.scrapers import NfceScraper
from scrapers.database import save_invoice
from repositories import (
    InvoiceRepository,
    CompanyRepository,
    ProductRepository,
    ItemRepository,
)

__all__ = ["router"]

router = APIRouter(prefix="/invoices")


@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_invoices(
    service: Annotated[InvoiceService, Depends(get_invoices_services)]
) -> list[InvoiceModel]:

    return service.find_all()


@router.get("/{id}", status_code=status.HTTP_200_OK)
async def get_invoice(
    id: Annotated[int, Depends(validate_id_input)],
    service: Annotated[InvoiceService, Depends(get_invoices_services)],
) -> None:

    invoice = service.find_by_id(id)

    return invoice


@router.patch("/{id}", status_code=status.HTTP_200_OK)
async def update_invoice(
    id: Annotated[int, Depends(validate_id_input)],
    invoice: InvoicePatchRequestModel,
    service: Annotated[InvoiceService, Depends(get_invoices_services)],
) -> None:

    service.update(id, invoice)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_invoice(
    invoice: InvoicePostRequestModel,
    service: Annotated[InvoiceService, Depends(get_invoices_services)],
) -> InvoiceModel:
    entity = service.save(invoice)

    return InvoiceModel.from_entity(entity)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_invoice(
    id: Annotated[int, Depends(validate_id_input)],
    service: Annotated[InvoiceService, Depends(get_invoices_services)],
) -> None:
    """Delete a invoice by it's ID

    Args:
        id (int): The invoice ID
    """

    service.delete(id)


@router.get("/companies/{id}", status_code=status.HTTP_200_OK)
async def get_all_invoices_by_company(
    id: Annotated[int, Depends(validate_id_input)],
    service: Annotated[InvoiceService, Depends(get_invoices_services)],
) -> list[InvoiceModel]:

    return service.find_by_company(id)


@router.get("/users/{id}", status_code=status.HTTP_200_OK)
async def get_all_invoices_by_user(
    id: Annotated[int, Depends(validate_id_input)],
    service: Annotated[InvoiceService, Depends(get_invoices_services)],
) -> list[InvoiceModel]:

    return service.find_by_user(id)


@router.post("/scrape", status_code=status.HTTP_201_CREATED)
async def scrape_and_save_invoice(
    body: ScrapeInvoiceRequestModel,
    invoice_repo: Annotated[InvoiceRepository, Depends(get_invoices_repository)],
    company_repo: Annotated[CompanyRepository, Depends(get_companies_repository)],
    product_repo: Annotated[ProductRepository, Depends(get_products_repository)],
    item_repo: Annotated[ItemRepository, Depends(get_items_repository)],
) -> dict[str, str]:
    try:
        scraper = NfceScraper()
        invoice_data = scraper.get(body.url)
        
        save_invoice(
            invoice=invoice_data,
            invoice_repository=invoice_repo,
            company_repository=company_repo,
            product_repository=product_repo,
            item_repository=item_repo,
        )
        return {"status": "success", "message": "NFC-e processada e salva com sucesso!"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao processar NFC-e: {str(e)}",
        )

