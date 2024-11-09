def generate_text_to_speech(text, client):
    """Generate audio file from text using ElevenLabs"""
    try:
        audio = client.generate(
            text=text,
            voice="Eric",
            model="eleven_turbo_v2_5"
        )
        return audio
    except Exception as e:
        print(f"Error generating audio: {e}")
        return None 