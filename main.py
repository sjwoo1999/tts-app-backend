from google.cloud import texttospeech
import functions_framework

@functions_framework.http
def generate_tts(request):
    request_json = request.get_json(silent=True)
    if not request_json or 'ssml' not in request_json:
        return 'SSML 필요', 400
    
    client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(ssml=request_json['ssml'])
    voice = texttospeech.VoiceSelectionParams(
        language_code="ko-KR",
        name="ko-KR-Wavenet-A",
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    # CORS 헤더 추가
    headers = {
        'Content-Type': 'audio/mp3',
        'Access-Control-Allow-Origin': '*'  # 모든 도메인 허용
    }
    return (response.audio_content, 200, headers)