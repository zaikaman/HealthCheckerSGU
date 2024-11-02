from io import BytesIO
import pyttsx3
from pydub import AudioSegment

def text_to_speech(text, lang='vi'):
    audio_data = BytesIO()
    try:
        # Khởi tạo engine
        engine = pyttsx3.init()

        # Thiết lập giọng đọc (chọn giọng nam nếu có)
        voices = engine.getProperty('voices')
        for voice in voices:
            if 'male' in voice.name.lower() or 'nam' in voice.name.lower():  # Chọn giọng nam
                engine.setProperty('voice', voice.id)
                break

        # Thiết lập tốc độ đọc
        engine.setProperty('rate', 200)  # Tăng tốc độ lên 200

        # Lưu âm thanh thành tệp tạm
        temp_filename = 'temp_audio.mp3'
        engine.save_to_file(text, temp_filename)
        engine.runAndWait()

        # Đọc tệp tạm và lưu vào BytesIO
        sound = AudioSegment.from_file(temp_filename, format="mp3")
        sound.export(audio_data, format="mp3")
        audio_data.seek(0)

        return audio_data
    except Exception as e:
        print("Lỗi khi chuyển văn bản thành giọng nói:", e)
        return None