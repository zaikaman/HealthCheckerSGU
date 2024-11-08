def stream_text_to_speech(text, client):
    audio_stream = client.generate(
        text=text,
        voice="Eric",
        model="eleven_turbo_v2_5",
        stream=True
    )
    return audio_stream 