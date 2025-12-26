from paddleocr import PaddleOCR
from fastapi import UploadFile
import tempfile
import os

ocr = PaddleOCR(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
)

async def extract_text_from_image(image: UploadFile) -> list[str]:
    
    suffix = os.path.splitext(image.filename)[-1]

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await image.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        result = ocr.predict(tmp_path)

        texts: list[str] = []
        for res in result:
            if "rec_texts" in res and isinstance(res["rec_texts"], list):
                texts.extend(res["rec_texts"])

        return texts

    finally:
        os.remove(tmp_path)