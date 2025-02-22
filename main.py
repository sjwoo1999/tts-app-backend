from google.cloud import texttospeech
import functions_framework
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 환경 변수 설정
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_CREDENTIALS_PATH")

@functions_framework.http
def generate_tts(request):
    request_json = request.get_json(silent=True)
    if not request_json or 'ssml' not in request_json:
        return 'SSML 또는 텍스트를 입력해주세요.', 400

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
    return response.audio_content, 200, {'Content-Type': 'audio/mp3'}