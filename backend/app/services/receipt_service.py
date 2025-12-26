from fastapi import UploadFile, HTTPException
from app.services.ocr_service import extract_text_from_image
from app.services.gemini_service import chat
from app.models.receipt import ReceiptCreate, ReceiptInDB
from app.core.database import get_database
from bson import ObjectId
import json
import re
from datetime import datetime


async def create_receipt_from_image(image: UploadFile) -> ReceiptInDB:

    texts = await extract_text_from_image(image)

    if not texts:
        raise HTTPException(
            status_code=400,
            detail="OCR failed to extract text"
        )

    ocr_text = "\n".join(texts)

    prompt = f"""
Berikut adalah teks hasil OCR dari struk belanja:

{ocr_text}

Tolong ubah menjadi JSON dengan field:
- merchant_name
- date (ISO format)
- total (integer)
- items (product_name, qty, price)

Kembalikan HANYA JSON valid.
"""

    result = chat(prompt)

    json_match = re.search(r'\{.*\}', result, re.DOTALL)
    if not json_match:
        raise HTTPException(
            status_code=500,
            detail="Gemini response does not contain JSON"
        )

    try:
        receipt_dict = json.loads(json_match.group())
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="Invalid JSON from Gemini"
        )

    receipt = ReceiptCreate(**receipt_dict)

    doc = receipt.model_dump()
    db = get_database()
    result = await db.receipts.insert_one(doc)

    doc["_id"] = str(result.inserted_id)
    return ReceiptInDB(**doc)
