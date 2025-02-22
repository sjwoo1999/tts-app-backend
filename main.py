from google.cloud import texttospeech
import functions_framework

@functions_framework.http
def generate_tts(request):
    # CORS 헤더 기본 설정
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST',
        'Access-Control-Allow-Headers': 'Content-Type'
    }

    # OPTIONS 요청 처리
    if request.method == 'OPTIONS':
        return ('', 204, headers)

    request_json = request.get_json(silent=True)
    if not request_json or 'ssml' not in request_json:
        return ('SSML 필요', 400, headers)

    try:
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
        headers['Content-Type'] = 'audio/mp3'
        return (response.audio_content, 200, headers)
    except Exception as e:
        return (f'에러: {str(e)}', 500, headers)  # 에러 메시지 반환