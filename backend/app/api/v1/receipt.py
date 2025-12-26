from fastapi import APIRouter, UploadFile, File
from app.services.receipt_service import create_receipt_from_image
from app.models.receipt import ReceiptInDB

router = APIRouter(prefix="/receipts", tags=["Receipts"])


@router.post("/scan", response_model=ReceiptInDB)
async def scan_receipt(image: UploadFile = File(...)):
    return await create_receipt_from_image(image)
