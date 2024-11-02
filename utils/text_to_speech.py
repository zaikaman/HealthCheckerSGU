# text_to_speech.py
from gtts import gTTS
from io import BytesIO

def text_to_speech(text, lang='vi'):
    audio_data = BytesIO()
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.write_to_fp(audio_data)
        audio_data.seek(0)  # Đặt con trỏ về đầu file để đọc lại
        return audio_data
    except Exception as e:
        print("Lỗi khi chuyển văn bản thành giọng nói:", e)
        return None
