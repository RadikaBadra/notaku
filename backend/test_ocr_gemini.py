from app.services.gemini_service import chat
from app.services.ocr_service import extract_text_from_image
import json
import re

try:
  texts = extract_text_from_image("sample-receipt.jpeg")
  
  if not texts:
    print("Error: No text extracted from image")
    exit(1)
  
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
  
  # Extract JSON from the response
  json_match = re.search(r'\{.*\}', result, re.DOTALL)
  if json_match:
    json_str = json_match.group()
    parsed_json = json.loads(json_str)
    print(json.dumps(parsed_json, indent=2))
  else:
    print("Error: No JSON found in response")
except FileNotFoundError:
  print("Error: Image file not found")
except Exception as e:
  print(f"Error: {str(e)}")