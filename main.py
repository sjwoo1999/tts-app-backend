from google.cloud import texttospeech
import functions_framework
import json

@functions_framework.http
def generate_tts(request):
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST',
        'Access-Control-Allow-Headers': 'Content-Type'
    }
    if request.method == 'OPTIONS':
        return ('', 204, headers)

    request_json = request.get_json(silent=True)
    if not request_json:
        return ('요청 데이터 필요', 400, headers)

    try:
        if 'ssml' in request_json:
            ssml = request_json['ssml']
        elif 'segments' in request_json:
            segments = request_json['segments']
            ssml = '<speak>'
            for segment in segments:
                text = segment.get('text', '')
                rate = segment.get('rate', '1.0')
                emphasis = segment.get('emphasis', 'none')
                break_time = segment.get('break', '0ms')
                pitch = segment.get('pitch', '0.0')  # 소리 파동 효과 추가
                ssml += f'<prosody rate="{rate}" pitch="{pitch}">'
                if emphasis != 'none':
                    ssml += f'<emphasis level="{emphasis}">{text}</emphasis>'
                else:
                    ssml += text
                ssml += f'</prosody><break time="{break_time}"/>'
            ssml += '</speak>'
        else:
            return ('SSML 또는 segments 필요', 400, headers)

        client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.SynthesisInput(ssml=ssml)
        
        language_code = request_json.get('language', 'ko-KR')
        voice_name = request_json.get('voice', 'ko-KR-Wavenet-A')
        voice = texttospeech.VoiceSelectionParams(
            language_code=language_code,
            name=voice_name
        )
        # 소리 파동 효과로 피치, 속도 커스터마이징
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            pitch=float(request_json.get('pitch', 0.0)),  # -20.0 ~ 20.0
            speaking_rate=float(request_json.get('rate', 1.0))  # 0.25 ~ 4.0
        )
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        headers['Content-Type'] = 'audio/mp3'
        return (response.audio_content, 200, headers)
    except Exception as e:
        return (f'에러: {str(e)}', 500, headers)