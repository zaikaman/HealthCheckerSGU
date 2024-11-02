# text_to_speech.py

from gtts import gTTS
import tempfile
import playsound

def text_to_speech(text, lang='vi'):
    """
    Chuyển văn bản thành giọng nói và phát âm thanh nhanh nhất có thể.

    Args:
        text (str): Văn bản cần chuyển đổi.
        lang (str): Ngôn ngữ của văn bản. Mặc định là tiếng Việt ('vi').

    Returns:
        None
    """
    try:
        # Chuyển đổi văn bản thành âm thanh
        tts = gTTS(text=text, lang=lang, slow=False)
        
        # Lưu tệp âm thanh tạm thời
        with tempfile.NamedTemporaryFile(delete=True, suffix='.mp3') as temp_file:
            temp_file_path = temp_file.name
            tts.save(temp_file_path)
            
            # Phát âm thanh ngay lập tức
            playsound.playsound(temp_file_path)
            
    except Exception as e:
        print("Lỗi khi chuyển văn bản thành giọng nói:", e)