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
            # SSML에서 <prosody> 태그 제거 (자연스러움 최적화)
            ssml = ssml.replace('<prosody rate="', '').replace('pitch="', '').replace('">', '>')
            ssml = ssml.replace('</prosody>', '')
        elif 'segments' in request_json:
            segments = request_json['segments']
            ssml = '<speak>'
            for segment in segments:
                text = segment.get('text', '')
                emphasis = segment.get('emphasis', 'none')
                break_time = segment.get('break', '0ms')
                # 피치/속도 제거, 자연스러운 기본값 사용
                ssml += '<prosody rate="1.0" pitch="0.0">'  # 고정값으로 자연스러움 보장
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
        
        # 기본 목소리로 고정 (자연스러운 여성 목소리)
        language_code = request_json.get('language', 'ko-KR')
        voice_name = 'ko-KR-Wavenet-A'  # 자연스러운 기본 목소리로 고정
        voice = texttospeech.VoiceSelectionParams(
            language_code=language_code,
            name=voice_name
        )
        # 자연스러운 목소리 기본 설정
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            pitch=0.0,  # 고정 피치
            speaking_rate=1.0  # 고정 속도
        )
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        headers['Content-Type'] = 'audio/mp3'
        return (response.audio_content, 200, headers)
    except Exception as e:
        return (f'에러: {str(e)}', 500, headers)