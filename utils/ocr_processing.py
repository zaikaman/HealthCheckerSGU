from PIL import Image
import pytesseract

# Đường dẫn tới tesseract.exe
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_image(filepath, lang='vie'):
    """Extract text from an image file using Tesseract OCR."""
    image = Image.open(filepath)
    text = pytesseract.image_to_string(image, lang=lang)
    return text
