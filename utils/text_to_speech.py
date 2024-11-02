# text_to_speech.py

from gtts import gTTS
import os

def text_to_speech(text, lang='vi', output_path="output.mp3"):
    """
    Chuyển văn bản thành giọng nói và lưu vào tệp mp3.

    Args:
        text (str): Văn bản cần chuyển đổi.
        lang (str): Ngôn ngữ của văn bản. Mặc định là tiếng Việt ('vi').
        output_path (str): Đường dẫn để lưu tệp âm thanh.

    Returns:
        str: Đường dẫn đến tệp âm thanh đã lưu.
    """
    try:
        # Chuyển đổi văn bản thành âm thanh và lưu tệp
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(output_path)
        return output_path
    except Exception as e:
        print("Lỗi khi chuyển văn bản thành giọng nói:", e)
        return None
