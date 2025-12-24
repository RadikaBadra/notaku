from paddleocr import PaddleOCR

ocr = PaddleOCR(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
)

def extract_text_from_image(image_path: str) -> list[str]:
    result = ocr.predict(image_path)

    texts: list[str] = []
    for res in result:
        if "rec_texts" in res and isinstance(res["rec_texts"], list):
            texts.extend(res["rec_texts"])

    return texts
