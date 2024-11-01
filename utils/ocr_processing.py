from PIL import Image
import pytesseract

def extract_text_from_image(filepath, lang='vie'):
    """Extract text from an image file using Tesseract OCR."""
    image = Image.open(filepath)
    # Directly use pytesseract without specifying the Tesseract path
    text = pytesseract.image_to_string(image, lang=lang)
    return text
