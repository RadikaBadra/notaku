from fastapi import APIRouter, UploadFile, File, Depends
from typing import List

from app.services.receipt_service import ReceiptService
from app.dependencies.auth import get_current_user_id
from app.models.receipt import ReceiptInDB, ReceiptCreate

router = APIRouter(
    prefix="/receipts",
    tags=["Receipts"],
)

@router.post("/scan", response_model=ReceiptInDB)
async def scan_receipt(
    image: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
):
    return await ReceiptService.create_receipt_from_image(
        image=image,
        user_id=user_id,
    )


@router.post("/create", response_model=ReceiptInDB)
async def create_receipt(
    receipt: ReceiptCreate,
    user_id: str = Depends(get_current_user_id),
):
    return await ReceiptService.create(receipt, user_id)


@router.put("/update/{receipt_id}", response_model=ReceiptInDB)
async def update_receipt(
    receipt_id: str,
    receipt: ReceiptCreate,
    user_id: str = Depends(get_current_user_id),
):
    return await ReceiptService.update(
        receipt_id=receipt_id,
        receipt=receipt,
        user_id=user_id,
    )


@router.get("/me", response_model=List[ReceiptInDB])
async def get_my_receipts(
    user_id: str = Depends(get_current_user_id),
):
    return await ReceiptService.get_by_user(user_id)


@router.get("/{receipt_id}", response_model=ReceiptInDB)
async def get_receipt_by_id(
    receipt_id: str,
    user_id: str = Depends(get_current_user_id),
):
    return await ReceiptService.get_by_id(receipt_id, user_id)
