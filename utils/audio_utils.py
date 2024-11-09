def generate_text_to_speech(text, client):
    """Generate audio file from text using ElevenLabs"""
    try:
        # Generate audio as bytes
        audio_generator = client.generate(
            text=text,
            voice="Eric",
            model="eleven_turbo_v2_5"
        )
        
        # Convert generator to bytes
        audio_bytes = b''.join(chunk for chunk in audio_generator)
        return audio_bytes
        
    except Exception as e:
        print(f"Error generating audio: {e}")
        return None