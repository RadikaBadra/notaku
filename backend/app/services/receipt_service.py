from fastapi import UploadFile, HTTPException
from app.services.ocr_service import extract_text_from_image
from app.services.gemini_service import chat
from app.models.receipt import ReceiptCreate, ReceiptInDB
from app.core.database import get_database
from bson import ObjectId
import json
import re


class ReceiptService:

    @staticmethod
    async def create_receipt_from_image(image: UploadFile, user_id: str) -> ReceiptInDB:
        texts = await extract_text_from_image(image)

        if not texts:
            raise HTTPException(status_code=400, detail="No text extracted from image")

        ocr_text = "\n".join(texts)

        prompt = f"""
        Berikut adalah teks hasil OCR dari struk belanja:

        {ocr_text}

        Tolong ubah menjadi JSON dengan field:
        - merchant_name
        - date
        - total
        - items (product_name, qty, price)
        """

        result = chat(prompt)

        json_match = re.search(r'\{.*\}', result, re.DOTALL)
        if not json_match:
            raise HTTPException(
                status_code=500,
                detail="Failed to parse receipt data from OCR text"
            )

        receipt_data = json.loads(json_match.group())

        receipt_create = ReceiptCreate(**receipt_data)

        return await ReceiptService.create(receipt_create, user_id)

    @staticmethod
    async def create(data: ReceiptCreate, user_id: str) -> ReceiptInDB:
        db = get_database()

        doc = data.model_dump()
        doc["user_id"] = user_id
        result = await db.receipts.insert_one(doc)
        
        doc["_id"] = str(result.inserted_id)

        return ReceiptInDB(**doc)
    
    @staticmethod
    async def update(receipt_id: str, data: ReceiptCreate, user_id: str) -> ReceiptInDB:
        db = get_database()

        doc = data.model_dump()
        doc["user_id"] = user_id

        result = await db.receipts.update_one(
            {"_id": ObjectId(receipt_id), "user_id": user_id},
            {"$set": doc}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Receipt not found")

        return ReceiptInDB(**doc, id=receipt_id)
    
    @staticmethod
    async def get_by_user(user_id: str) -> list[ReceiptInDB]:
        db = get_database()

        receipts_cursor = db.receipts.find({"user_id": user_id})
        receipts = []
        async for receipt_doc in receipts_cursor:
            receipts.append(ReceiptInDB(**receipt_doc, id=str(receipt_doc["_id"])))

        return receipts
    
    @staticmethod
    async def get_by_id(receipt_id: str, user_id: str) -> ReceiptInDB:
        db = get_database()

        receipt_doc = await db.receipts.find_one(
            {"_id": ObjectId(receipt_id), "user_id": user_id}
        )

        if not receipt_doc:
            raise HTTPException(status_code=404, detail="Receipt not found")

        return ReceiptInDB(**receipt_doc, id=str(receipt_doc["_id"]))
    
    @staticmethod
    async def delete(receipt_id: str, user_id: str) -> None:
        db = get_database()

        result = await db.receipts.delete_one(
            {"_id": ObjectId(receipt_id), "user_id": user_id}
        )

        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Receipt not found")
        
        return None
